"""
AUREXIS - LLM Base Interface
All providers MUST implement this interface.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, AsyncGenerator, Optional


class BaseLLM(ABC):
    name: str = "base"
    description: str = ""

    @abstractmethod
    async def complete(self, prompt: str) -> str:
        """Single completion"""
        pass

    @abstractmethod
    async def chat(self, system: str, messages: List[Dict], tools: List[Dict] = None) -> str:
        """Chat completion"""
        pass

    @abstractmethod
    async def stream(self, system: str, messages: List[Dict], tools: List[Dict] = None) -> AsyncGenerator[str, None]:
        """Streaming chat"""
        yield ""

    def is_available(self) -> bool:
        """Check if this LLM is ready to use"""
        return True
