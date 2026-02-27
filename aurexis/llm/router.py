"""
AUREXIS - LLM Router
Selects and instantiates the right LLM based on config.
"""
import json
from pathlib import Path
from llm.registry import LLMRegistry
from llm.base import BaseLLM


class LLMRouter:
    def __init__(self):
        self._cache: dict = {}

    def get(self, name: str) -> BaseLLM:
        if name in self._cache:
            return self._cache[name]
        
        cls = LLMRegistry.get_class(name)
        if cls is None:
            raise ValueError(f"LLM '{name}' not registered. Available: {list(LLMRegistry._providers.keys())}")
        
        # Load per-LLM config if available
        config = self._load_llm_config(name)
        try:
            instance = cls(**config)
        except TypeError:
            instance = cls()
        
        self._cache[name] = instance
        return instance

    def _load_llm_config(self, name: str) -> dict:
        p = Path("config/config.json")
        if p.exists():
            cfg = json.loads(p.read_text())
            return cfg.get("llm_configs", {}).get(name, {})
        return {}
