"""AUREXIS - Mistral Provider"""
from llm.base import BaseLLM
from typing import List, Dict, AsyncGenerator
from core.auth import KeyVault


class MistralLLM(BaseLLM):
    name = "mistral"
    description = "Mistral AI (mistral-large, mistral-small)"

    def __init__(self, model: str = "mistral-small-latest"):
        self.model = model

    def is_available(self) -> bool:
        return bool(KeyVault().get_key("mistral"))

    async def complete(self, prompt: str) -> str:
        return await self.chat("You are a helpful assistant.", [{"role": "user", "content": prompt}])

    async def chat(self, system: str, messages: List[Dict], tools=None) -> str:
        from mistralai.async_client import MistralAsyncClient
        from mistralai.models.chat_completion import ChatMessage
        client = MistralAsyncClient(api_key=KeyVault().get_key("mistral"))
        msgs = [ChatMessage(role="system", content=system)] + \
               [ChatMessage(role=m["role"], content=m["content"]) for m in messages]
        resp = await client.chat(model=self.model, messages=msgs)
        return resp.choices[0].message.content

    async def stream(self, system: str, messages: List[Dict], tools=None) -> AsyncGenerator[str, None]:
        response = await self.chat(system, messages, tools)
        yield response
