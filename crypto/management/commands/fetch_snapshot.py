from django.core.management.base import BaseCommand

from crypto.models import CoinPrice, Snapshot
from providers.coingecko import CoinGeckoProvider


class Command(BaseCommand):
    help = "Загружает снимок рынка с CoinGecko и сохраняет в БД"

    # Что делает — получает данные из API, создаёт снимок, привязывает цены
    def handle(self, *args, **options):
        self.stdout.write("Загружаю данные с CoinGecko...")

        provider = CoinGeckoProvider(per_page=10)
        assets = provider.get_assets()

        snapshot = Snapshot.objects.create()  # создаю запись в БД через Django ORM

        for asset in assets:
            CoinPrice.objects.create(  # создаем цену, привязывая к снимку
                snapshot=snapshot,
                name=asset.name,
                symbol=asset.symbol,
                price=asset.price,
                change_24h=asset.change_24h,
            )

        self.stdout.write(self.style.SUCCESS(f"Снимок #{snapshot.id} создан! Сохранено {len(assets)} монет."))
