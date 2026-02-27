"""AUREXIS - Kimi (Moonshot) Provider — OpenAI-compatible"""
from llm.providers.custom_provider import CustomOpenAILLM
from core.auth import KeyVault


class KimiLLM(CustomOpenAILLM):
    name = "kimi"
    description = "Kimi / Moonshot AI (OpenAI-compatible)"

    def __init__(self):
        super().__init__(
            base_url="https://api.moonshot.cn/v1",
            model="moonshot-v1-8k",
            api_key_name="kimi"
        )
