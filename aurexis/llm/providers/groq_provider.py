"""AUREXIS - Groq Provider"""
from llm.base import BaseLLM
from typing import List, Dict, AsyncGenerator
from core.auth import KeyVault


class GroqLLM(BaseLLM):
    name = "groq"
    description = "Groq (llama3, mixtral — ultra fast inference)"

    def __init__(self, model: str = "llama3-70b-8192"):
        self.model = model

    def is_available(self) -> bool:
        return bool(KeyVault().get_key("groq"))

    async def complete(self, prompt: str) -> str:
        return await self.chat("You are a helpful assistant.", [{"role": "user", "content": prompt}])

    async def chat(self, system: str, messages: List[Dict], tools=None) -> str:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=KeyVault().get_key("groq"))
        resp = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}] + messages
        )
        return resp.choices[0].message.content

    async def stream(self, system: str, messages: List[Dict], tools=None) -> AsyncGenerator[str, None]:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=KeyVault().get_key("groq"))
        stream = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}] + messages,
            stream=True
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
