"""
AUREXIS - Provider: Phi-2 Local (llama-cpp-python)
"""
from __future__ import annotations
import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional

from llm.base import BaseLLM, LLMConfig, LLMMessage, LLMResponse
from config.settings import BASE_DIR

MODELS_DIR = BASE_DIR / "models"
DEFAULT_MODEL = "phi-2.Q4_K_M.gguf"


class Phi2LocalLLM(BaseLLM):

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self._llm = None

    async def initialize(self) -> bool:
        if self._initialized:
            return True
        
        model_path = MODELS_DIR / (self.config.model or DEFAULT_MODEL)
        
        if not model_path.exists():
            print(f"[WARN] Modèle local non trouvé: {model_path}")
            print(f"[INFO] Téléchargez le modèle depuis: https://huggingface.co/microsoft/phi-2")
            return False
        
        try:
            from llama_cpp import Llama
            self._llm = await asyncio.to_thread(
                Llama,
                model_path=str(model_path),
                n_ctx=self.config.context_window,
                n_threads=4,
                n_gpu_layers=0,  # CPU only pour compatibilité 4GB RAM
                verbose=False,
            )
            self._initialized = True
            return True
        except ImportError:
            print("[ERROR] llama-cpp-python non installé. Run: pip install llama-cpp-python")
            return False
        except Exception as e:
            print(f"[ERROR] Erreur chargement Phi-2: {e}")
            return False

    async def chat(
        self,
        messages: list[LLMMessage],
        tools: Optional[list[dict]] = None,
    ) -> LLMResponse:
        if not self._initialized:
            await self.initialize()
        
        if self._llm is None:
            return LLMResponse(
                content="⚠️ Modèle Phi-2 non disponible. Vérifiez que le fichier GGUF est dans /models/",
                provider=self.provider_id,
                model=self.config.model,
            )

        prompt = self._build_prompt(messages)
        
        response = await asyncio.to_thread(
            self._llm,
            prompt,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            stop=["<|endoftext|>", "User:", "Human:"],
        )
        
        content = response["choices"][0]["text"].strip()
        tokens = response.get("usage", {}).get("total_tokens", 0)
        
        return LLMResponse(
            content=content,
            provider=self.provider_id,
            model=self.config.model,
            tokens_used=tokens,
        )

    async def stream(self, messages: list[LLMMessage]) -> AsyncGenerator[str, None]:
        if not self._initialized:
            await self.initialize()
        
        if self._llm is None:
            yield "⚠️ Modèle Phi-2 non disponible."
            return

        prompt = self._build_prompt(messages)
        
        loop = asyncio.get_event_loop()
        queue: asyncio.Queue = asyncio.Queue()

        def _run():
            for chunk in self._llm(
                prompt,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                stream=True,
                stop=["<|endoftext|>", "User:", "Human:"],
            ):
                token = chunk["choices"][0].get("text", "")
                loop.call_soon_threadsafe(queue.put_nowait, token)
            loop.call_soon_threadsafe(queue.put_nowait, None)

        asyncio.get_event_loop().run_in_executor(None, _run)
        
        while True:
            token = await queue.get()
            if token is None:
                break
            yield token

    def _build_prompt(self, messages: list[LLMMessage]) -> str:
        """Construit le prompt au format Phi-2."""
        parts = []
        for msg in messages:
            if msg.role == "system":
                parts.append(f"Instruct: {msg.content}\nOutput:")
            elif msg.role == "user":
                parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                parts.append(f"Assistant: {msg.content}")
        parts.append("Assistant:")
        return "\n".join(parts)
