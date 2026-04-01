from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from app.models.chat import MessageRole


class ChatSessionCreate(BaseModel):
    title: Optional[str] = "Yeni Sohbet"


class ChatSessionResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ChatSessionListResponse(BaseModel):
    sessions: List[ChatSessionResponse]
    total: int


class MessageSource(BaseModel):
    document_id: int
    filename: str
    chunk_text: str
    score: float
    page: Optional[int] = None


class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    role: MessageRole
    content: str
    sources: Optional[List[MessageSource]] = None
    tokens_used: Optional[int] = None
    latency_ms: Optional[int] = None
    model_used: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    session_id: int
    messages: List[ChatMessageResponse]


class WSMessageIn(BaseModel):
    content: str
    session_id: int


class WSMessageOut(BaseModel):
    type: str  # "token", "sources", "done", "error"
    content: Optional[str] = None
    sources: Optional[List[MessageSource]] = None
    message_id: Optional[int] = None
    error: Optional[str] = None
