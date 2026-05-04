import typer
import formatters
from providers.factory import ProviderFactory
from formatters.factory import FormatterFactory
from models.portfolio import CryptoPortfolio
from storage.factory import StorageFactory
from settings import Settings

app = typer.Typer()


@app.command()
def analyze(
    source: str = typer.Option("coingecko", "--source", "-s", help="Источник данных: coingecko или coinmarketcap"),
    output: str = typer.Option("console", "--output", "-o", help="Формат вывода: console, json или csv"),
    top: int = typer.Option(3, "--top", "-t", help="Количество лидеров роста/падения"),
):
    """Анализирует рынок криптовалют и выводит результат."""
    
    # 1. Получаем данные через провайдер
    provider = ProviderFactory.create(source)
    assets = provider.get_assets()

    # 2. Анализируем через портфель
    portfolio = CryptoPortfolio(assets)
    gainers = portfolio.top_gainers(top)
    losers = portfolio.top_losers(top)

    # 3. Выводим через форматтер
    formatter = FormatterFactory.create(output)
    formatter.format(gainers, losers)

    # 4. Сохраняем через хранилище
    settings = Settings()
    storage = StorageFactory.create(settings)
    results = {
        "top_gainers": [
            {"name": a.name, "symbol": a.symbol, "price": a.price, "change_24h": a.change_24h}
            for a in gainers
        ],
        "top_losers": [
            {"name": a.name, "symbol": a.symbol, "price": a.price, "change_24h": a.change_24h}
            for a in losers
        ],
    }
    storage.save(results)

@app.command()
def list_snapshots():
    """Выводит список всех сохранённых снимков."""
    from storage.sqlite_storage import SqliteStorage
    storage = SqliteStorage()
    snapshots = storage.list_snapshots()
    
    if not snapshots:
        print("Снимков пока нет.")
        return
    
    print(f"{'ID':<5} {'Дата и время'}")
    print("-" * 30)
    for s in snapshots:
        print(f"{s['id']:<5} {s['created_at']}")

@app.command()
def compare_snapshots(
    id1: int = typer.Argument(..., help="ID первого снимка"),
    id2: int = typer.Argument(..., help="ID второго снимка"),
):
    """Сравнивает два снимка по ID."""
    from storage.sqlite_storage import SqliteStorage
    storage = SqliteStorage()
    result = storage.compare_snapshots(id1, id2)
    
    if not result:
        print("Нет данных для сравнения.")
        return
    
    print(f"Сравнение снимков {id1} → {id2}:")
    print(f"{'Монета':<20} {'Цена до':<12} {'Цена после':<12} {'Разница':<10}")
    print("-" * 55)
    for r in result:
        print(f"{r['name']:<20} ${r['price_old']:<11.2f} ${r['price_new']:<11.2f} {r['diff_percent']:+.2f}%")


if __name__ == "__main__":
    app()