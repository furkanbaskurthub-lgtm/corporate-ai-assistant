import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from app.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class DocumentChunk:
    text: str
    metadata: Dict[str, Any]
    chunk_index: int


class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_text_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        pages = []
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                if text.strip():
                    pages.append({
                        "text": text,
                        "page": page_num + 1,
                        "total_pages": len(doc),
                    })
            doc.close()
        except Exception as e:
            logger.error("pdf_extraction_failed", file_path=file_path, error=str(e))
            raise ValueError(f"PDF işlenirken hata oluştu: {str(e)}")
        return pages

    def extract_text_from_txt(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            return [{"text": content, "page": 1, "total_pages": 1}]
        except Exception as e:
            logger.error("txt_extraction_failed", file_path=file_path, error=str(e))
            raise ValueError(f"Dosya okunurken hata oluştu: {str(e)}")

    def split_text_into_chunks(
        self,
        text: str,
        metadata: Dict[str, Any],
        start_index: int = 0,
    ) -> List[DocumentChunk]:
        chunks = []
        start = 0
        chunk_index = start_index

        text = text.strip()
        if not text:
            return chunks

        while start < len(text):
            end = start + self.chunk_size

            if end < len(text):
                # Cümle sınırında kes
                for sep in ["\n\n", "\n", ". ", " "]:
                    boundary = text.rfind(sep, start, end)
                    if boundary > start:
                        end = boundary + len(sep)
                        break

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        text=chunk_text,
                        metadata={**metadata, "chunk_index": chunk_index},
                        chunk_index=chunk_index,
                    )
                )
                chunk_index += 1

            start = end - self.chunk_overlap
            if start >= len(text):
                break

        return chunks

    def process_file(self, file_path: str, document_id: int, filename: str) -> List[DocumentChunk]:
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension == ".pdf":
            pages = self.extract_text_from_pdf(file_path)
        elif extension in [".txt", ".log"]:
            pages = self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Desteklenmeyen dosya formatı: {extension}")

        all_chunks = []
        chunk_offset = 0

        for page_data in pages:
            metadata = {
                "document_id": document_id,
                "filename": filename,
                "page": page_data.get("page", 1),
                "total_pages": page_data.get("total_pages", 1),
            }
            chunks = self.split_text_into_chunks(
                text=page_data["text"],
                metadata=metadata,
                start_index=chunk_offset,
            )
            all_chunks.extend(chunks)
            chunk_offset += len(chunks)

        logger.info(
            "document_processed",
            document_id=document_id,
            filename=filename,
            total_chunks=len(all_chunks),
        )
        return all_chunks


document_processor = DocumentProcessor()
