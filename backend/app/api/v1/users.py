from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.ai.vector_store import vector_store
from app.ai.llm_manager import llm_manager
from app.core.security import get_current_user_id

router = APIRouter(prefix="/users", tags=["Kullanıcılar"])


@router.get("/stats")
async def get_user_stats(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from app.db.repositories.document_repo import DocumentRepository
    from app.db.repositories.chat_repo import ChatRepository

    doc_repo = DocumentRepository(db)
    chat_repo = ChatRepository(db)

    doc_count = await doc_repo.count_by_user(user_id)
    session_count = await chat_repo.count_sessions_by_user(user_id)
    vector_stats = vector_store.get_stats(user_id)

    return {
        "document_count": doc_count,
        "chat_session_count": session_count,
        "vector_chunks": vector_stats["total_vectors"],
    }


@router.get("/models")
async def get_available_models(user_id: int = Depends(get_current_user_id)):
    return {"models": llm_manager.get_available_models()}
