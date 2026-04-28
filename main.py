import typer
from providers.factory import ProviderFactory
from formatters.factory import FormatterFactory
from models.portfolio import CryptoPortfolio
from storage.json_storage import JsonStorage

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

    # 3. Выводим через форматтер
    formatter = FormatterFactory.create(output)
    formatter.format(gainers)

    # 4. Сохраняем результаты через хранилище
    storage = JsonStorage()
    results = {
        "top_gainers": [
            {"name": a.name, "symbol": a.symbol, "change_24h": a.change_24h}
            for a in gainers
        ]
    }
    storage.save(results)


if __name__ == "__main__":
    app()