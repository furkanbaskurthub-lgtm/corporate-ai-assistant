import json
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.chat_service import ChatService
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionListResponse,
    ChatHistoryResponse,
    WSMessageIn,
    WSMessageOut,
)
from app.core.security import get_current_user_id, decode_token
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["Sohbet"])


@router.post("/sessions", response_model=ChatSessionResponse, status_code=201)
async def create_session(
    data: ChatSessionCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    return await service.create_session(user_id, data)


@router.get("/sessions", response_model=ChatSessionListResponse)
async def get_sessions(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    return await service.get_sessions(user_id)


@router.get("/sessions/{session_id}/messages", response_model=ChatHistoryResponse)
async def get_messages(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    return await service.get_session_messages(session_id, user_id)


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    await service.delete_session(session_id, user_id)


@router.websocket("/ws/{session_id}")
async def chat_websocket(session_id: int, websocket: WebSocket):
    await websocket.accept()

    # Token doğrulama
    token = websocket.query_params.get("token")
    if not token:
        await websocket.send_json({"type": "error", "error": "Token gerekli"})
        await websocket.close(code=1008)
        return

    payload = decode_token(token)
    if not payload:
        await websocket.send_json({"type": "error", "error": "Geçersiz token"})
        await websocket.close(code=1008)
        return

    user_id = int(payload.get("sub", 0))

    logger.info("websocket_connected", user_id=user_id, session_id=session_id)

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            question = data.get("content", "").strip()
            model = data.get("model")

            if not question:
                await websocket.send_json({"type": "error", "error": "Mesaj boş olamaz"})
                continue

            from app.db.database import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                service = ChatService(db)
                try:
                    async for chunk in service.process_message_stream(
                        user_id=user_id,
                        session_id=session_id,
                        question=question,
                        model=model,
                    ):
                        await websocket.send_json(chunk)
                    await db.commit()
                except HTTPException as e:
                    await websocket.send_json({"type": "error", "error": e.detail})
                except Exception as e:
                    logger.error("websocket_error", error=str(e))
                    await websocket.send_json({"type": "error", "error": str(e)})

    except WebSocketDisconnect:
        logger.info("websocket_disconnected", user_id=user_id, session_id=session_id)
    except Exception as e:
        logger.error("websocket_unexpected_error", error=str(e))
