import typer
import providers
import formatters
from providers.factory import ProviderFactory
from formatters.factory import FormatterFactory
from models.portfolio import CryptoPortfolio

app = typer.Typer()


@app.command()
def analyze(
    source: str = typer.Option("coingecko", "--source", "-s", help="Источник данных: coingecko или coinmarketcap"),
    output: str = typer.Option("console", "--output", "-o", help="Формат вывода: console, json или csv"),
    top: int = typer.Option(3, "--top", "-t", help="Количество лидеров роста/падения"),
):
    """Анализирует рынок криптовалют и выводит результат."""
    
    provider = ProviderFactory.create(source)
    assets = provider.get_assets()

    portfolio = CryptoPortfolio(assets)
    gainers = portfolio.top_gainers(top)
    losers = portfolio.top_losers(top)

    formatter = FormatterFactory.create(output)
    formatter.format(gainers, losers)


if __name__ == "__main__":
    app()