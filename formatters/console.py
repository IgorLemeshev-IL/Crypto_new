from rich.console import Console
from rich.table import Table
from models.crypto_asset import CryptoAsset
from formatters.base import OutputFormatter


class ConsoleFormatter(OutputFormatter):
    def __init__(self):
        self.console = Console()

    def format(self, gainers: list[CryptoAsset], losers: list[CryptoAsset]) -> None:
        self._print_table("🚀 Топ лидеров роста (24ч)", "green", gainers)
        self.console.print()
        self._print_table("📉 Топ лидеров падения (24ч)", "red", losers)

    def _print_table(self, title: str, style: str, assets: list[CryptoAsset]) -> None:
        if not assets:
            self.console.print("[yellow]Нет данных[/yellow]")
            return
        table = Table(title=title, style=style)
        table.add_column("Монета", style="bold")
        table.add_column("Символ", style="dim")
        table.add_column("Цена USD", justify="right")
        table.add_column("Изменение 24ч", justify="right")
        for a in assets:
            color = "green" if a.change_24h > 0 else "red" if a.change_24h < 0 else "white"
            table.add_row(a.name, a.symbol.upper(), f"${a.price:,.2f}", f"[{color}]{a.change_24h:+.2f}%[/{color}]")
        self.console.print(table)