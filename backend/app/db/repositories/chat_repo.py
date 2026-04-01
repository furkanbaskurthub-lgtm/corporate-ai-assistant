from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from app.models.chat import ChatSession, ChatMessage, MessageRole


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, user_id: int, title: str = "Yeni Sohbet") -> ChatSession:
        session = ChatSession(user_id=user_id, title=title)
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def get_session_by_id(self, session_id: int) -> Optional[ChatSession]:
        result = await self.db.execute(
            select(ChatSession).where(ChatSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_session_by_id_and_user(self, session_id: int, user_id: int) -> Optional[ChatSession]:
        result = await self.db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_sessions_by_user(self, user_id: int) -> List[ChatSession]:
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_session_title(self, session_id: int, title: str) -> Optional[ChatSession]:
        session = await self.get_session_by_id(session_id)
        if session:
            session.title = title
            await self.db.flush()
            await self.db.refresh(session)
        return session

    async def delete_session(self, session_id: int, user_id: int) -> bool:
        session = await self.get_session_by_id_and_user(session_id, user_id)
        if session:
            await self.db.delete(session)
            await self.db.flush()
            return True
        return False

    async def add_message(
        self,
        session_id: int,
        role: MessageRole,
        content: str,
        sources: Optional[list] = None,
        tokens_used: Optional[int] = None,
        latency_ms: Optional[int] = None,
        model_used: Optional[str] = None,
    ) -> ChatMessage:
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            sources=sources,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
            model_used=model_used,
        )
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def get_messages_by_session(self, session_id: int, limit: int = 50) -> List[ChatMessage]:
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_sessions_by_user(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count(ChatSession.id)).where(ChatSession.user_id == user_id)
        )
        return result.scalar_one()
