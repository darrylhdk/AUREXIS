"""
AUREXIS - Key Vault (encrypted API key storage)
"""
import json
from pathlib import Path
from cryptography.fernet import Fernet


class KeyVault:
    def __init__(self, key_file="config/secret.key", vault_file="config/api_keys.enc"):
        self.vault_file = Path(vault_file)
        key_path = Path(key_file)
        if not key_path.exists():
            raise FileNotFoundError("secret.key missing. Run install.py first.")
        self._fernet = Fernet(key_path.read_bytes())

    def _load(self) -> dict:
        if not self.vault_file.exists():
            return {}
        try:
            return json.loads(self._fernet.decrypt(self.vault_file.read_bytes()))
        except Exception:
            return {}

    def _save(self, data: dict):
        self.vault_file.write_bytes(self._fernet.encrypt(json.dumps(data).encode()))

    def set_key(self, provider: str, key: str):
        data = self._load()
        data[provider] = key
        self._save(data)

    def get_key(self, provider: str) -> str:
        return self._load().get(provider, "")

    def list_providers(self) -> list:
        return list(self._load().keys())

    def delete_key(self, provider: str):
        data = self._load()
        data.pop(provider, None)
        self._save(data)
