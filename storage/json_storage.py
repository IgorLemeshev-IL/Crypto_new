import json
from datetime import datetime
from storage.base import BaseStorage


class JsonStorage(BaseStorage):
    """Сохраняет результаты в JSON-файл."""

    def __init__(self, filename: str = "crypto_report.json"):
        self.filename = filename

    def save(self, results: dict) -> None:
        results["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)