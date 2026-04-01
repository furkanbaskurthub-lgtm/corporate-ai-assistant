import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import faiss
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class VectorStore:
    """
    Kullanıcıya özel FAISS indeksleri yöneten sınıf.
    Her kullanıcının kendi vektör indeksi vardır.
    """

    def __init__(self, store_dir: str):
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self._indices: Dict[int, faiss.IndexFlatIP] = {}
        self._metadata: Dict[int, List[Dict[str, Any]]] = {}

    def _get_index_path(self, user_id: int) -> Path:
        return self.store_dir / f"user_{user_id}" / "index.faiss"

    def _get_metadata_path(self, user_id: int) -> Path:
        return self.store_dir / f"user_{user_id}" / "metadata.pkl"

    def _user_dir(self, user_id: int) -> Path:
        user_dir = self.store_dir / f"user_{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def _load_index(self, user_id: int) -> Tuple[Optional[faiss.IndexFlatIP], List[Dict]]:
        index_path = self._get_index_path(user_id)
        metadata_path = self._get_metadata_path(user_id)

        if not index_path.exists() or not metadata_path.exists():
            return None, []

        try:
            index = faiss.read_index(str(index_path))
            with open(metadata_path, "rb") as f:
                metadata = pickle.load(f)
            return index, metadata
        except Exception as e:
            logger.error("load_index_failed", user_id=user_id, error=str(e))
            return None, []

    def _save_index(self, user_id: int, index: faiss.IndexFlatIP, metadata: List[Dict]):
        self._user_dir(user_id)
        index_path = self._get_index_path(user_id)
        metadata_path = self._get_metadata_path(user_id)

        faiss.write_index(index, str(index_path))
        with open(metadata_path, "wb") as f:
            pickle.dump(metadata, f)

    def _get_or_create_index(self, user_id: int) -> Tuple[faiss.IndexFlatIP, List[Dict]]:
        if user_id not in self._indices:
            index, metadata = self._load_index(user_id)
            if index is None:
                # Inner product (cosine similarity için normalize vektörler kullanılır)
                index = faiss.IndexFlatIP(1536)
                metadata = []
            self._indices[user_id] = index
            self._metadata[user_id] = metadata
        return self._indices[user_id], self._metadata[user_id]

    def add_document_embeddings(
        self,
        user_id: int,
        document_id: int,
        embeddings: List[List[float]],
        chunks_metadata: List[Dict[str, Any]],
    ) -> int:
        index, metadata = self._get_or_create_index(user_id)

        vectors = np.array(embeddings, dtype=np.float32)
        # Cosine similarity için normalize et
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        vectors = vectors / norms

        index.add(vectors)

        for chunk_meta in chunks_metadata:
            metadata.append({**chunk_meta, "document_id": document_id})

        self._save_index(user_id, index, metadata)

        logger.info(
            "embeddings_added",
            user_id=user_id,
            document_id=document_id,
            count=len(embeddings),
        )
        return len(embeddings)

    def search(
        self,
        user_id: int,
        query_embedding: List[float],
        top_k: int = 5,
        document_ids: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        index, metadata = self._get_or_create_index(user_id)

        if index.ntotal == 0:
            return []

        query_vec = np.array([query_embedding], dtype=np.float32)
        norm = np.linalg.norm(query_vec)
        if norm > 0:
            query_vec = query_vec / norm

        # Fazladan çek, filtrele
        k = min(top_k * 3, index.ntotal)
        scores, indices = index.search(query_vec, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(metadata):
                continue
            chunk_meta = metadata[idx]

            if document_ids and chunk_meta.get("document_id") not in document_ids:
                continue

            results.append({
                **chunk_meta,
                "score": float(score),
            })

            if len(results) >= top_k:
                break

        return results

    def delete_document_embeddings(self, user_id: int, document_id: int) -> bool:
        """
        FAISS IndexFlatIP silmeyi desteklemediği için yeniden inşa ediyoruz.
        """
        index, metadata = self._get_or_create_index(user_id)

        if not metadata:
            return False

        keep_indices = [
            i for i, m in enumerate(metadata) if m.get("document_id") != document_id
        ]

        if len(keep_indices) == len(metadata):
            return False  # Silinecek doküman yok

        if not keep_indices:
            # Tüm verileri temizle
            new_index = faiss.IndexFlatIP(1536)
            new_metadata = []
        else:
            # Kalan vektörleri yeniden ekle
            old_vectors = faiss.rev_swig_ptr(index.get_xb(), index.ntotal * 1536).reshape(
                index.ntotal, 1536
            )
            kept_vectors = old_vectors[keep_indices]
            new_index = faiss.IndexFlatIP(1536)
            new_index.add(kept_vectors)
            new_metadata = [metadata[i] for i in keep_indices]

        self._indices[user_id] = new_index
        self._metadata[user_id] = new_metadata
        self._save_index(user_id, new_index, new_metadata)

        logger.info(
            "document_embeddings_deleted",
            user_id=user_id,
            document_id=document_id,
            remaining_chunks=len(new_metadata),
        )
        return True

    def get_stats(self, user_id: int) -> Dict[str, int]:
        index, metadata = self._get_or_create_index(user_id)
        return {
            "total_vectors": index.ntotal,
            "total_chunks": len(metadata),
        }


vector_store = VectorStore(settings.VECTOR_STORE_DIR)
