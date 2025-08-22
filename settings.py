import json
import os
from typing import Dict, Any


class AppSettings:
    DEFAULT_DATA: Dict[str, Any] = {
        "trigger_button": "mouse4",
        "spam_button": "ЛКМ",
        "original_resolution": {"width": "", "height": "", "refresh": ""},
        "desired_resolution": {"width": "", "height": "", "refresh": ""},
        "click_interval_ms": 60,
    }

    def __init__(self, filename: str = "settings.json") -> None:
        self.filename = filename
        self.data: Dict[str, Any] = dict(self.DEFAULT_DATA)
        self.load()

    def load(self) -> None:
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                if isinstance(raw, dict):
                    merged = dict(self.DEFAULT_DATA)
                    merged.update(raw)
                    self.data = merged
            except (OSError, json.JSONDecodeError):
                pass

    def save(self) -> None:
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def set_click_interval(self, ms: int) -> None:
        self.data["click_interval_ms"] = max(1, ms)
        self.save()

    def get_click_interval(self) -> float:
        return self.data.get("click_interval_ms", 60) / 1000.0

