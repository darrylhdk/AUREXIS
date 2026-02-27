"""
AUREXIS - Configuration centrale
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"
PROMPTS_DIR = BASE_DIR / "prompts"
ASSETS_DIR = BASE_DIR / "assets"

DATA_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

CONFIG_FILE = CONFIG_DIR / "aurexis.json"
USER_FILE = DATA_DIR / "user.json"
KEYS_FILE = DATA_DIR / ".keys.enc"


class AurexisSettings(BaseSettings):
    app_name: str = "AUREXIS"
    version: str = "1.0.0"
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    default_llm: str = "phi2_local"
    default_mode: str = "assistant"
    secret_key: str = Field(default="CHANGE_ME_IN_PRODUCTION_32chars!!")

    class Config:
        env_file = str(BASE_DIR / ".env")
        extra = "ignore"


settings = AurexisSettings()


def load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def save_config(data: dict):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_config(key: str, default=None):
    cfg = load_config()
    return cfg.get(key, default)


def set_config(key: str, value):
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
