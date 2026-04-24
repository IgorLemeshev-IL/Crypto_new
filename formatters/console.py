from rich.console import Console
from rich.table import Table
from models.crypto_asset import CryptoAsset
from formatters.base import OutputFormatter


class ConsoleFormatter(OutputFormatter):
    """Вывод результатов в консоль с Rich-таблицами."""

    def __init__(self):
        self.console = Console()

    def format(self, assets: list[CryptoAsset]) -> None:
        if not assets:
            self.console.print("[yellow]Нет данных для отображения[/yellow]")
            return

        table = Table(title="📊 Результаты анализа")
        table.add_column("Монета", style="bold")
        table.add_column("Символ", style="dim")
        table.add_column("Цена USD", justify="right")
        table.add_column("Изменение 24ч", justify="right")

        for a in assets:
            color = "green" if a.change_24h > 0 else "red" if a.change_24h < 0 else "white"
            table.add_row(
                a.name,
                a.symbol.upper(),
                f"${a.price:,.2f}",
                f"[{color}]{a.change_24h:+.2f}%[/{color}]"
            )

        self.console.print(table)