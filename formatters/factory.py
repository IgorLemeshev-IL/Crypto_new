from formatters.base import OutputFormatter


class FormatterFactory:
    _formatters: dict[str, type[OutputFormatter]] = {}

    @classmethod
    def register(cls, name: str, formatter_class: type[OutputFormatter]) -> None:
        cls._formatters[name] = formatter_class

    @classmethod
    def create(cls, name: str) -> OutputFormatter:
        formatter_class = cls._formatters.get(name)
        if formatter_class is None:
            raise ValueError(f"Unknown formatter: {name}")
        return formatter_class()
