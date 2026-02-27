"""AUREXIS - Custom OpenAI-compatible API Provider"""
from llm.base import BaseLLM
from typing import List, Dict, AsyncGenerator
from core.auth import KeyVault


class CustomOpenAILLM(BaseLLM):
    name = "custom"
    description = "Any OpenAI-compatible API"

    def __init__(self, base_url: str = "", model: str = "gpt-3.5-turbo", api_key_name: str = "custom"):
        self.base_url = base_url
        self.model = model
        self.api_key_name = api_key_name

    def _client(self):
        from openai import AsyncOpenAI
        return AsyncOpenAI(
            api_key=KeyVault().get_key(self.api_key_name) or "no-key",
            base_url=self.base_url or None
        )

    def is_available(self) -> bool:
        return bool(self.base_url or KeyVault().get_key(self.api_key_name))

    async def complete(self, prompt: str) -> str:
        return await self.chat("You are a helpful assistant.", [{"role": "user", "content": prompt}])

    async def chat(self, system: str, messages: List[Dict], tools=None) -> str:
        client = self._client()
        resp = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}] + messages
        )
        return resp.choices[0].message.content

    async def stream(self, system: str, messages: List[Dict], tools=None) -> AsyncGenerator[str, None]:
        client = self._client()
        stream = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}] + messages,
            stream=True
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
