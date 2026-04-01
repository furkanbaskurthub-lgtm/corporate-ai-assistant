import os
import uuid
import asyncio
from pathlib import Path
from typing import List, Optional
from fastapi import HTTPException, UploadFile, status
import aiofiles

from app.db.repositories.document_repo import DocumentRepository
from app.models.document import DocumentStatus
from app.schemas.document import DocumentResponse, DocumentListResponse, DocumentDeleteResponse
from app.ai.document_processor import document_processor
from app.ai.embeddings import embedding_manager
from app.ai.vector_store import vector_store
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class DocumentService:
    def __init__(self, db):
        self.repo = DocumentRepository(db)

    def _get_upload_dir(self, user_id: int) -> Path:
        user_upload_dir = Path(settings.UPLOAD_DIR) / f"user_{user_id}"
        user_upload_dir.mkdir(parents=True, exist_ok=True)
        return user_upload_dir

    def _validate_file(self, file: UploadFile) -> str:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dosya adı bulunamadı",
            )
        ext = Path(file.filename).suffix.lstrip(".").lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Desteklenmeyen dosya formatı. İzin verilenler: {', '.join(settings.ALLOWED_EXTENSIONS)}",
            )
        return ext

    async def upload_document(self, user_id: int, file: UploadFile) -> DocumentResponse:
        ext = self._validate_file(file)

        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Dosya boyutu {settings.MAX_FILE_SIZE // 1024 // 1024}MB'yi aşamaz",
            )

        upload_dir = self._get_upload_dir(user_id)
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        file_path = upload_dir / unique_filename

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        doc = await self.repo.create(
            user_id=user_id,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=len(content),
            file_type=ext,
        )

        logger.info(
            "document_uploaded",
            user_id=user_id,
            doc_id=doc.id,
            filename=file.filename,
            size=len(content),
        )

        # Arka planda işle
        asyncio.create_task(self._process_document(doc.id, user_id, str(file_path), file.filename))

        return DocumentResponse.model_validate(doc)

    async def _process_document(
        self, doc_id: int, user_id: int, file_path: str, original_filename: str
    ):
        from app.db.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            repo = DocumentRepository(db)
            try:
                await repo.update_status(doc_id, DocumentStatus.PROCESSING)
                await db.commit()

                # Chunk'lara böl
                chunks = document_processor.process_file(file_path, doc_id, original_filename)

                if not chunks:
                    await repo.update_status(
                        doc_id,
                        DocumentStatus.FAILED,
                        error_message="Dosyadan metin çıkarılamadı",
                    )
                    await db.commit()
                    return

                # Embedding oluştur
                texts = [c.text for c in chunks]
                embeddings = await embedding_manager.embed_batch(texts)

                # FAISS'e kaydet
                chunks_metadata = [c.metadata for c in chunks]
                vector_store.add_document_embeddings(
                    user_id=user_id,
                    document_id=doc_id,
                    embeddings=embeddings,
                    chunks_metadata=chunks_metadata,
                )

                await repo.update_status(doc_id, DocumentStatus.READY, chunk_count=len(chunks))
                await db.commit()

                logger.info(
                    "document_processing_complete",
                    doc_id=doc_id,
                    chunks=len(chunks),
                )

            except Exception as e:
                logger.error("document_processing_failed", doc_id=doc_id, error=str(e))
                try:
                    await repo.update_status(
                        doc_id,
                        DocumentStatus.FAILED,
                        error_message=str(e)[:500],
                    )
                    await db.commit()
                except Exception:
                    pass

    async def get_documents(self, user_id: int) -> DocumentListResponse:
        docs = await self.repo.get_all_by_user(user_id)
        return DocumentListResponse(
            documents=[DocumentResponse.model_validate(d) for d in docs],
            total=len(docs),
        )

    async def delete_document(self, doc_id: int, user_id: int) -> DocumentDeleteResponse:
        doc = await self.repo.get_by_id_and_user(doc_id, user_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doküman bulunamadı",
            )

        # Dosyayı sil
        try:
            if os.path.exists(doc.file_path):
                os.remove(doc.file_path)
        except Exception as e:
            logger.warning("file_delete_failed", file_path=doc.file_path, error=str(e))

        # Vektör store'dan sil
        vector_store.delete_document_embeddings(user_id=user_id, document_id=doc_id)

        # DB'den sil
        await self.repo.delete(doc_id, user_id)

        logger.info("document_deleted", doc_id=doc_id, user_id=user_id)
        return DocumentDeleteResponse(message="Doküman başarıyla silindi", document_id=doc_id)
