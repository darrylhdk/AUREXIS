"""
AUREXIS - Agent abstraction layer
High-level interface over the orchestrator for external connectors.
"""
from typing import Optional


class AurexisAgent:
    """
    Lightweight facade over the Orchestrator.
    Used by connectors (Telegram, Discord, etc.) for clean integration.
    """
    def __init__(self, orchestrator):
        self.orch = orchestrator

    async def ask(self, text: str, session_id: Optional[str] = None) -> str:
        """Process a user message and return a response"""
        return await self.orch.process(text)

    async def ask_stream(self, text: str):
        """Stream response chunks"""
        async for chunk in self.orch.process_stream(text):
            yield chunk

    @property
    def mode(self):
        return self.orch.active_mode

    @property
    def llm(self):
        return self.orch.active_llm
