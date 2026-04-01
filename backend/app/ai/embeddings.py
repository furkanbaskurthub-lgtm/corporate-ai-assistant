import asyncio
from typing import List, Optional
import numpy as np
from openai import AsyncOpenAI
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class EmbeddingManager:
    def __init__(self):
        self._client: Optional[AsyncOpenAI] = None
        self.model = settings.OPENAI_EMBEDDING_MODEL
        self.dimension = 1536  # text-embedding-ada-002 boyutu

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client

    async def embed_text(self, text: str) -> List[float]:
        text = text.replace("\n", " ").strip()
        if not text:
            return [0.0] * self.dimension

        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error("embedding_failed", text_length=len(text), error=str(e))
            raise

    async def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            cleaned = [t.replace("\n", " ").strip() for t in batch]

            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=cleaned,
                )
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)

                logger.info(
                    "batch_embedded",
                    batch_start=i,
                    batch_size=len(batch),
                    total=len(texts),
                )
            except Exception as e:
                logger.error("batch_embedding_failed", batch_start=i, error=str(e))
                raise

            # Rate limiting
            if i + batch_size < len(texts):
                await asyncio.sleep(0.1)

        return all_embeddings

    def normalize(self, vectors: List[List[float]]) -> np.ndarray:
        arr = np.array(vectors, dtype=np.float32)
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        return arr / norms


embedding_manager = EmbeddingManager()
