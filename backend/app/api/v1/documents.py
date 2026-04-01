from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.document_service import DocumentService
from app.schemas.document import DocumentResponse, DocumentListResponse, DocumentDeleteResponse
from app.core.security import get_current_user_id

router = APIRouter(prefix="/documents", tags=["Dokümanlar"])


@router.post("/upload", response_model=DocumentResponse, status_code=202)
async def upload_document(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentService(db)
    return await service.upload_document(user_id, file)


@router.get("/", response_model=DocumentListResponse)
async def get_documents(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentService(db)
    return await service.get_documents(user_id)


@router.delete("/{doc_id}", response_model=DocumentDeleteResponse)
async def delete_document(
    doc_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentService(db)
    return await service.delete_document(doc_id, user_id)
