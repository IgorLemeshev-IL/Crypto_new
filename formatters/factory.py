from formatters.console import ConsoleFormatter
from formatters.json import JSONFormatter
from formatters.csv import CSVFormatter
from formatters.base import OutputFormatter


class FormatterFactory:
    """Фабрика форматтеров — создаёт нужный форматтер по имени."""

    @staticmethod
    def create(name: str) -> OutputFormatter:
        if name == "console":
            return ConsoleFormatter()
        if name == "json":
            return JSONFormatter()
        if name == "csv":
            return CSVFormatter()
        raise ValueError(f"Unknown formatter: {name}")