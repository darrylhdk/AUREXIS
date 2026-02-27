"""
AUREXIS - Local LLM via llama-cpp-python (Phi-2, Mistral, etc.)
"""
from llm.base import BaseLLM
from typing import List, Dict, AsyncGenerator
import asyncio
from pathlib import Path


class LocalLLM(BaseLLM):
    name = "phi2_local"
    description = "Phi-2 GGUF (local, no API key needed)"

    def __init__(self, model_path: str = "models/phi-2.Q4_K_M.gguf",
                 n_ctx: int = 2048, n_threads: int = 4):
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self._model = None

    def _get_model(self):
        if self._model is None:
            from llama_cpp import Llama
            self._model = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                verbose=False
            )
        return self._model

    def is_available(self) -> bool:
        return Path(self.model_path).exists()

    async def complete(self, prompt: str) -> str:
        model = self._get_model()
        output = await asyncio.to_thread(
            lambda: model(prompt, max_tokens=512, stop=["</s>", "Human:", "User:"])
        )
        return output["choices"][0]["text"].strip()

    async def chat(self, system: str, messages: List[Dict], tools=None) -> str:
        prompt = f"System: {system}\n\n"
        for m in messages:
            role = "Human" if m["role"] == "user" else "Assistant"
            prompt += f"{role}: {m['content']}\n"
        prompt += "Assistant:"
        return await self.complete(prompt)

    async def stream(self, system: str, messages: List[Dict], tools=None) -> AsyncGenerator[str, None]:
        # llama.cpp supports streaming but we simplify here
        response = await self.chat(system, messages, tools)
        # Simulate streaming word by word
        for word in response.split(" "):
            yield word + " "
            await asyncio.sleep(0)
