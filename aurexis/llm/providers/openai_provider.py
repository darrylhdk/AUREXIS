"""AUREXIS - OpenAI Provider"""
import json
from llm.base import BaseLLM
from typing import List, Dict, AsyncGenerator
from core.auth import KeyVault


class OpenAILLM(BaseLLM):
    name = "openai"
    description = "OpenAI GPT-4o / GPT-4 / GPT-3.5"

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def _client(self):
        from openai import AsyncOpenAI
        return AsyncOpenAI(api_key=KeyVault().get_key("openai"))

    def is_available(self) -> bool:
        return bool(KeyVault().get_key("openai"))

    async def complete(self, prompt: str) -> str:
        return await self.chat("You are a helpful assistant.", [{"role": "user", "content": prompt}])

    async def chat(self, system: str, messages: List[Dict], tools=None) -> str:
        client = self._client()
        kwargs = {"model": self.model, "messages": [{"role": "system", "content": system}] + messages}
        if tools:
            kwargs["tools"] = [{"type": "function", "function": t} for t in tools]
            kwargs["tool_choice"] = "auto"
        resp = await client.chat.completions.create(**kwargs)
        choice = resp.choices[0]
        # Handle tool calls
        if choice.finish_reason == "tool_calls":
            tc = choice.message.tool_calls[0]
            return json.dumps({"type": "tool_call", "name": tc.function.name,
                               "args": json.loads(tc.function.arguments)})
        return choice.message.content or ""

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
