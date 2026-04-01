from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from app.models.document import Document, DocumentStatus


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: int,
        filename: str,
        original_filename: str,
        file_path: str,
        file_size: int,
        file_type: str,
    ) -> Document:
        doc = Document(
            user_id=user_id,
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            status=DocumentStatus.PENDING,
        )
        self.db.add(doc)
        await self.db.flush()
        await self.db.refresh(doc)
        return doc

    async def get_by_id(self, doc_id: int) -> Optional[Document]:
        result = await self.db.execute(select(Document).where(Document.id == doc_id))
        return result.scalar_one_or_none()

    async def get_by_id_and_user(self, doc_id: int, user_id: int) -> Optional[Document]:
        result = await self.db.execute(
            select(Document).where(Document.id == doc_id, Document.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_all_by_user(self, user_id: int) -> List[Document]:
        result = await self.db.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_ready_documents_by_user(self, user_id: int) -> List[Document]:
        result = await self.db.execute(
            select(Document).where(
                Document.user_id == user_id,
                Document.status == DocumentStatus.READY,
            )
        )
        return list(result.scalars().all())

    async def update_status(
        self,
        doc_id: int,
        status: DocumentStatus,
        chunk_count: int = 0,
        error_message: Optional[str] = None,
    ) -> Optional[Document]:
        doc = await self.get_by_id(doc_id)
        if doc:
            doc.status = status
            doc.chunk_count = chunk_count
            doc.error_message = error_message
            await self.db.flush()
            await self.db.refresh(doc)
        return doc

    async def delete(self, doc_id: int, user_id: int) -> bool:
        doc = await self.get_by_id_and_user(doc_id, user_id)
        if doc:
            await self.db.delete(doc)
            await self.db.flush()
            return True
        return False

    async def count_by_user(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count(Document.id)).where(Document.user_id == user_id)
        )
        return result.scalar_one()
