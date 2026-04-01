from typing import List, Optional, AsyncGenerator, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.chat_repo import ChatRepository
from app.db.repositories.document_repo import DocumentRepository
from app.models.chat import MessageRole
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionListResponse,
    ChatHistoryResponse,
    ChatMessageResponse,
    MessageSource,
)
from app.ai.rag_pipeline import rag_pipeline
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ChatService:
    def __init__(self, db: AsyncSession):
        self.chat_repo = ChatRepository(db)
        self.doc_repo = DocumentRepository(db)

    async def create_session(self, user_id: int, data: ChatSessionCreate) -> ChatSessionResponse:
        session = await self.chat_repo.create_session(user_id, data.title or "Yeni Sohbet")
        return ChatSessionResponse.model_validate(session)

    async def get_sessions(self, user_id: int) -> ChatSessionListResponse:
        sessions = await self.chat_repo.get_sessions_by_user(user_id)
        return ChatSessionListResponse(
            sessions=[ChatSessionResponse.model_validate(s) for s in sessions],
            total=len(sessions),
        )

    async def get_session_messages(self, session_id: int, user_id: int) -> ChatHistoryResponse:
        session = await self.chat_repo.get_session_by_id_and_user(session_id, user_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sohbet oturumu bulunamadı",
            )

        messages = await self.chat_repo.get_messages_by_session(session_id)
        return ChatHistoryResponse(
            session_id=session_id,
            messages=[ChatMessageResponse.model_validate(m) for m in messages],
        )

    async def delete_session(self, session_id: int, user_id: int):
        deleted = await self.chat_repo.delete_session(session_id, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sohbet oturumu bulunamadı",
            )

    async def _get_chat_history(self, session_id: int) -> List[Dict[str, str]]:
        messages = await self.chat_repo.get_messages_by_session(session_id, limit=20)
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]

    async def process_message(
        self,
        user_id: int,
        session_id: int,
        question: str,
        model: Optional[str] = None,
    ) -> ChatMessageResponse:
        session = await self.chat_repo.get_session_by_id_and_user(session_id, user_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sohbet oturumu bulunamadı",
            )

        # Kullanıcı mesajını kaydet
        user_msg = await self.chat_repo.add_message(
            session_id=session_id,
            role=MessageRole.USER,
            content=question,
        )

        # Sohbet geçmişini al
        history = await self._get_chat_history(session_id)

        # İlk sohbette başlığı güncelle
        if session.title == "Yeni Sohbet" and len(history) <= 1:
            new_title = question[:60] + ("..." if len(question) > 60 else "")
            await self.chat_repo.update_session_title(session_id, new_title)

        # RAG pipeline
        result = await rag_pipeline.query(
            user_id=user_id,
            question=question,
            chat_history=history[:-1],  # Yeni eklenen hariç
            model=model,
        )

        # Asistan cevabını kaydet
        assistant_msg = await self.chat_repo.add_message(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=result["answer"],
            sources=result["sources"],
            tokens_used=result.get("tokens_used"),
            latency_ms=result.get("latency_ms"),
            model_used=result.get("model_used"),
        )

        return ChatMessageResponse.model_validate(assistant_msg)

    async def process_message_stream(
        self,
        user_id: int,
        session_id: int,
        question: str,
        model: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        session = await self.chat_repo.get_session_by_id_and_user(session_id, user_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sohbet oturumu bulunamadı",
            )

        # Kullanıcı mesajını kaydet
        await self.chat_repo.add_message(
            session_id=session_id,
            role=MessageRole.USER,
            content=question,
        )

        history = await self._get_chat_history(session_id)

        if session.title == "Yeni Sohbet" and len(history) <= 1:
            new_title = question[:60] + ("..." if len(question) > 60 else "")
            await self.chat_repo.update_session_title(session_id, new_title)

        full_content = ""
        sources = []

        async for chunk in rag_pipeline.query_stream(
            user_id=user_id,
            question=question,
            chat_history=history[:-1],
            model=model,
        ):
            if chunk["type"] == "sources":
                sources = chunk["sources"]
                yield chunk
            elif chunk["type"] == "token":
                full_content += chunk["content"]
                yield chunk
            elif chunk["type"] == "done":
                # Asistan cevabını DB'ye kaydet
                assistant_msg = await self.chat_repo.add_message(
                    session_id=session_id,
                    role=MessageRole.ASSISTANT,
                    content=full_content,
                    sources=sources,
                    latency_ms=chunk.get("latency_ms"),
                )
                yield {
                    "type": "done",
                    "message_id": assistant_msg.id,
                    "latency_ms": chunk.get("latency_ms"),
                }
