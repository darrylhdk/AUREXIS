"""
AUREXIS - LLM Registry
Central catalogue of all available LLM providers.
To add a new LLM: register it here.
"""
from typing import Dict
from llm.base import BaseLLM


class LLMRegistry:
    _providers: Dict[str, type] = {}

    @classmethod
    def register(cls, name: str, provider_class: type):
        cls._providers[name] = provider_class

    @classmethod
    def get_class(cls, name: str):
        return cls._providers.get(name)

    def list_llms(self) -> dict:
        result = {}
        for name, cls in self._providers.items():
            try:
                instance = cls()
                result[name] = {
                    "description": instance.description,
                    "available": instance.is_available(),
                    "requires_api_key": name not in ("phi2_local",)
                }
            except Exception as e:
                result[name] = {"description": "", "available": False, "error": str(e)}
        return result


# ── Auto-register all providers ────────────────────────────────
def _register_all():
    from llm.providers.local import LocalLLM
    from llm.providers.openai_provider import OpenAILLM
    from llm.providers.anthropic_provider import AnthropicLLM
    from llm.providers.mistral_provider import MistralLLM
    from llm.providers.groq_provider import GroqLLM
    from llm.providers.kimi_provider import KimiLLM
    from llm.providers.custom_provider import CustomOpenAILLM

    LLMRegistry.register("phi2_local", LocalLLM)
    LLMRegistry.register("openai", OpenAILLM)
    LLMRegistry.register("anthropic", AnthropicLLM)
    LLMRegistry.register("mistral", MistralLLM)
    LLMRegistry.register("groq", GroqLLM)
    LLMRegistry.register("kimi", KimiLLM)
    LLMRegistry.register("custom", CustomOpenAILLM)

_register_all()
