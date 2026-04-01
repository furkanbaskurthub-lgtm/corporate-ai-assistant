import time
from typing import List, Dict, Any, Optional, AsyncGenerator
from app.ai.embeddings import embedding_manager
from app.ai.vector_store import vector_store
from app.ai.llm_manager import llm_manager
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class RAGPipeline:
    """
    RAG (Retrieval-Augmented Generation) pipeline.

    Akış:
    1. Kullanıcı sorusu → embedding
    2. FAISS'te semantik arama
    3. İlgili chunk'lar → context oluştur
    4. Context + soru + geçmiş → LLM
    5. Cevap + kaynaklar → kullanıcı
    """

    def __init__(self):
        self.top_k = settings.TOP_K_RESULTS

    def _build_context(self, search_results: List[Dict[str, Any]]) -> str:
        if not search_results:
            return ""

        context_parts = []
        for i, result in enumerate(search_results, 1):
            filename = result.get("filename", "Bilinmeyen dosya")
            page = result.get("page", "?")
            text = result.get("text", "")
            context_parts.append(
                f"[Kaynak {i}: {filename}, Sayfa {page}]\n{text}"
            )

        return "\n\n---\n\n".join(context_parts)

    def _format_sources(self, search_results: List[Dict[str, Any]]) -> List[Dict]:
        sources = []
        for result in search_results:
            sources.append({
                "document_id": result.get("document_id"),
                "filename": result.get("filename", ""),
                "chunk_text": result.get("text", "")[:300] + "..." if len(result.get("text", "")) > 300 else result.get("text", ""),
                "score": round(result.get("score", 0.0), 4),
                "page": result.get("page"),
            })
        return sources

    def _format_chat_history(self, history: List[Dict]) -> List[Dict[str, str]]:
        formatted = []
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                formatted.append({"role": role, "content": content})
        return formatted

    async def query(
        self,
        user_id: int,
        question: str,
        chat_history: Optional[List[Dict]] = None,
        document_ids: Optional[List[int]] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        start_time = time.time()
        chat_history = chat_history or []

        logger.info("rag_query_start", user_id=user_id, question_len=len(question))

        # 1. Soru embedding
        query_embedding = await embedding_manager.embed_text(question)

        # 2. Semantik arama
        search_results = vector_store.search(
            user_id=user_id,
            query_embedding=query_embedding,
            top_k=self.top_k,
            document_ids=document_ids,
        )

        # 3. Context oluştur
        context = self._build_context(search_results)
        sources = self._format_sources(search_results)
        history = self._format_chat_history(chat_history)

        # 4. LLM'e gönder
        result = await llm_manager.generate(
            question=question,
            context=context,
            chat_history=history,
            model=model,
        )

        latency_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "rag_query_done",
            user_id=user_id,
            sources_found=len(sources),
            latency_ms=latency_ms,
            tokens_used=result.get("tokens_used"),
        )

        return {
            "answer": result["content"],
            "sources": sources,
            "tokens_used": result.get("tokens_used"),
            "latency_ms": latency_ms,
            "model_used": result.get("model"),
        }

    async def query_stream(
        self,
        user_id: int,
        question: str,
        chat_history: Optional[List[Dict]] = None,
        document_ids: Optional[List[int]] = None,
        model: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        start_time = time.time()
        chat_history = chat_history or []

        # 1. Soru embedding
        query_embedding = await embedding_manager.embed_text(question)

        # 2. Semantik arama
        search_results = vector_store.search(
            user_id=user_id,
            query_embedding=query_embedding,
            top_k=self.top_k,
            document_ids=document_ids,
        )

        # 3. Kaynakları hemen gönder
        sources = self._format_sources(search_results)
        yield {"type": "sources", "sources": sources}

        # 4. Context oluştur
        context = self._build_context(search_results)
        history = self._format_chat_history(chat_history)

        # 5. Streaming LLM
        full_content = ""
        async for token in llm_manager.generate_stream(
            question=question,
            context=context,
            chat_history=history,
            model=model,
        ):
            full_content += token
            yield {"type": "token", "content": token}

        latency_ms = int((time.time() - start_time) * 1000)

        yield {
            "type": "done",
            "content": full_content,
            "latency_ms": latency_ms,
        }


rag_pipeline = RAGPipeline()
