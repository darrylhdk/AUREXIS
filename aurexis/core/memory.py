"""
AUREXIS - Conversation Memory
"""
from collections import deque
from typing import List, Dict
import json
from pathlib import Path


class ConversationMemory:
    def __init__(self, max_turns: int = 20, persist_path: str = "data/memory.json"):
        self.max_turns = max_turns
        self.persist_path = Path(persist_path)
        self._history: deque = deque(maxlen=max_turns * 2)
        self._load()

    def add_user(self, content: str):
        self._history.append({"role": "user", "content": content})
        self._save()

    def add_assistant(self, content: str):
        self._history.append({"role": "assistant", "content": content})
        self._save()

    def get_messages(self) -> List[Dict]:
        return list(self._history)

    def clear(self):
        self._history.clear()
        self._save()

    def _save(self):
        self.persist_path.parent.mkdir(exist_ok=True)
        self.persist_path.write_text(json.dumps(list(self._history)))

    def _load(self):
        if self.persist_path.exists():
            try:
                for msg in json.loads(self.persist_path.read_text()):
                    self._history.append(msg)
            except Exception:
                pass
