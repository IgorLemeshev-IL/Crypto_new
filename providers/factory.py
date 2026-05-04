from providers.base import CryptoProvider


class ProviderFactory:
    """Фабрика провайдеров — реестр (Registry pattern)."""

    _providers: dict[str, type[CryptoProvider]] = {}

    @classmethod
    def register(cls, name: str, provider_class: type[CryptoProvider]) -> None:
        cls._providers[name] = provider_class

    @classmethod
    def create(cls, name: str) -> CryptoProvider:
        provider_class = cls._providers.get(name)
        if provider_class is None:
            raise ValueError(f"Unknown provider: {name}")
        return provider_class()