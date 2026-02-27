"""AUREXIS - Anthropic Claude Provider"""
from llm.base import BaseLLM
from typing import List, Dict, AsyncGenerator
from core.auth import KeyVault


class AnthropicLLM(BaseLLM):
    name = "anthropic"
    description = "Anthropic Claude (Sonnet, Opus, Haiku)"

    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        self.model = model

    def _client(self):
        import anthropic
        return anthropic.AsyncAnthropic(api_key=KeyVault().get_key("anthropic"))

    def is_available(self) -> bool:
        return bool(KeyVault().get_key("anthropic"))

    async def complete(self, prompt: str) -> str:
        return await self.chat("You are a helpful assistant.", [{"role": "user", "content": prompt}])

    async def chat(self, system: str, messages: List[Dict], tools=None) -> str:
        client = self._client()
        kwargs = {"model": self.model, "max_tokens": 2048, "system": system, "messages": messages}
        if tools:
            kwargs["tools"] = [{"name": t["name"], "description": t.get("description",""),
                                 "input_schema": t.get("parameters", {})} for t in tools]
        resp = await client.messages.create(**kwargs)
        block = resp.content[0]
        if block.type == "tool_use":
            import json
            return json.dumps({"type": "tool_call", "name": block.name, "args": block.input})
        return block.text

    async def stream(self, system: str, messages: List[Dict], tools=None) -> AsyncGenerator[str, None]:
        client = self._client()
        async with client.messages.stream(
            model=self.model, max_tokens=2048, system=system, messages=messages
        ) as s:
            async for text in s.text_stream:
                yield text
