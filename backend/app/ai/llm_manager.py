from typing import AsyncGenerator, List, Dict, Optional
from openai import AsyncOpenAI
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

AVAILABLE_MODELS = {
    "gpt-3.5-turbo": {
        "name": "GPT-3.5 Turbo",
        "max_tokens": 4096,
        "context_window": 16385,
    },
    "gpt-4": {
        "name": "GPT-4",
        "max_tokens": 4096,
        "context_window": 8192,
    },
    "gpt-4-turbo-preview": {
        "name": "GPT-4 Turbo",
        "max_tokens": 4096,
        "context_window": 128000,
    },
}

SYSTEM_PROMPT = """Sen kurumsal bir AI asistanısın. Kullanıcının yüklediği dokümanlar üzerinden sorularını yanıtlıyorsun.

Kurallar:
1. Sadece sağlanan bağlamdan (context) cevap ver
2. Eğer bilgi bağlamda yoksa "Bu bilgi yüklü dokümanlarda bulunamadı." de
3. Cevapların kısa, net ve Türkçe olsun
4. Kaynak dokümanı belirtmen istendiğinde belirt
5. Tahmin yürütme, sadece dokümanlardaki bilgilere dayan"""


class LLMManager:
    def __init__(self):
        self._client: Optional[AsyncOpenAI] = None

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client

    def build_messages(
        self,
        question: str,
        context: str,
        chat_history: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if context:
            messages.append({
                "role": "system",
                "content": f"İlgili doküman içerikleri:\n\n{context}",
            })

        # Son 10 mesajı geçmiş olarak ekle (token tasarrufu)
        for msg in chat_history[-10:]:
            messages.append(msg)

        messages.append({"role": "user", "content": question})
        return messages

    async def generate(
        self,
        question: str,
        context: str,
        chat_history: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> Dict:
        model = model or settings.OPENAI_MODEL
        if model not in AVAILABLE_MODELS:
            model = settings.OPENAI_MODEL

        messages = self.build_messages(question, context, chat_history)

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            return {
                "content": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens if response.usage else None,
                "model": model,
            }
        except Exception as e:
            logger.error("llm_generate_failed", model=model, error=str(e))
            raise

    async def generate_stream(
        self,
        question: str,
        context: str,
        chat_history: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> AsyncGenerator[str, None]:
        model = model or settings.OPENAI_MODEL
        if model not in AVAILABLE_MODELS:
            model = settings.OPENAI_MODEL

        messages = self.build_messages(question, context, chat_history)

        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )

            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content
        except Exception as e:
            logger.error("llm_stream_failed", model=model, error=str(e))
            raise

    def get_available_models(self) -> List[Dict]:
        return [
            {"id": model_id, **info}
            for model_id, info in AVAILABLE_MODELS.items()
        ]


llm_manager = LLMManager()
