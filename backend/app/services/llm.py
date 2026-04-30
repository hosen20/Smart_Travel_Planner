"""LLM service for interacting with Groq or OpenAI."""

from __future__ import annotations

import os
from typing import Any, Dict, List

try:
    from openai import AsyncOpenAI
except ImportError:  # pragma: no cover
    AsyncOpenAI = None

from app.logging_config import get_logger
from app.settings import Settings

log = get_logger(__name__)


class LLMService:
    """Service for LLM interactions."""

    def __init__(self, settings: Settings):
        self.settings = settings
        if settings.llm_provider == "mock":
            self.client = None
            return

        if AsyncOpenAI is None:
            raise RuntimeError(
                "The openai package is required for LLMService. Install it with `pip install openai`."
            )

        if settings.llm_provider == "groq":
            self.client = AsyncOpenAI(
                api_key=settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1",
            )
        else:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]] | None = None, **kwargs) -> Dict[str, Any]:
        """Generate a response from the LLM."""
        try:
            if self.settings.llm_provider == "mock":
                last_user = next((msg for msg in reversed(messages) if msg["role"] == "user"), None)
                prompt = last_user["content"] if last_user else "Hello"
                return {"role": "assistant", "content": f"Mock reply for: {prompt}"}

            response = await self.client.chat.completions.create(
                model=self.settings.model_name(),
                messages=messages,
                tools=tools,
                **kwargs
            )
            message = response.choices[0].message
            return {
                "role": message.role,
                "content": message.content,
                "tool_calls": message.tool_calls
            }
        except Exception as e:
            log.error("LLM generation failed", error=str(e))
            raise

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts."""
        try:
            if self.settings.llm_provider == "groq":
                if self.settings.openai_api_key:
                    openai_client = AsyncOpenAI(api_key=self.settings.openai_api_key)
                    response = await openai_client.embeddings.create(
                        input=texts,
                        model=self.settings.openai_embedding_model,
                    )
                    return [emb.embedding for emb in response.data]

                try:
                    from sentence_transformers import SentenceTransformer
                except ImportError as import_error:
                    raise RuntimeError(
                        "Groq provider requires either OPENAI_API_KEY for embeddings or optional sentence-transformers installed. "
                        "Install with `uv install --group embeddings` or set OPENAI_API_KEY."
                    ) from import_error

                model = SentenceTransformer("all-MiniLM-L6-v2")
                return model.encode(texts).tolist()

            if self.settings.llm_provider == "mock":
                return [[float(len(text))] * 8 for text in texts]

            response = await self.client.embeddings.create(
                input=texts,
                model=self.settings.embedding_model_name()
            )
            return [emb.embedding for emb in response.data]
        except Exception as e:
            log.error("Embedding generation failed", error=str(e))
            raise

    async def aclose(self) -> None:
        """Close the underlying LLM client if supported."""
        if hasattr(self.client, "aclose"):
            await self.client.aclose()