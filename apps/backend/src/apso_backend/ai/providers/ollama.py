from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class OllamaProvider:
    base_url: str
    chat_model: str
    embedding_model: str
    timeout_seconds: int = 120

    async def health(self) -> dict[str, Any]:
        url = self.base_url.rstrip("/") + "/api/tags"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    async def generate_json(self, prompt: str, schema: dict[str, Any] | None = None) -> dict[str, Any]:
        url = self.base_url.rstrip("/") + "/api/generate"
        payload: dict[str, Any] = {
            "model": self.chat_model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0,
            },
        }
        if schema:
            payload["schema"] = schema

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        url = self.base_url.rstrip("/") + "/api/embed"
        payload = {"model": self.embedding_model, "input": texts}
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("embeddings", [])
