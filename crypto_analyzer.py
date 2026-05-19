import json
import time
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Any

import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


def retry(max_attempts: int = 3, delay: int = 2):
    """Повторяет запрос при ошибке сети."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as e:  # type: ignore[misc]
                    last_exception = e
                    if attempt < max_attempts:
                        console.print(f"[yellow]⚠ Попытка {attempt}/{max_attempts} не удалась. Повтор через {delay}с...[/yellow]")
                        time.sleep(delay)
            raise last_exception

        return wrapper

    return decorator


def _sort_key(item: dict[str, Any]) -> float:
    return float(item.get("price_change_percentage_24h") or 0)


@retry(max_attempts=3, delay=2)
def fetch_crypto_data(url: str | None = None):
    if url is None:
        url = "https://api.coingecko.com/api/v3/coins/markets"
    params: dict[str, str | int] = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 50, "page": 1}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def analyze_data(data: list[dict]) -> dict:
    top_gainers = sorted(data, key=_sort_key, reverse=True)[:3]
    top_losers = sorted(data, key=_sort_key)[:3]
    highest_volume = max(data, key=lambda x: x.get("total_volume") or 0)
    total_market_cap = sum(coin.get("market_cap") or 0 for coin in data)
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_coins_analyzed": len(data),
        "total_market_cap_usd": total_market_cap,
        "top_gainers": [
            {"name": c["name"], "symbol": c["symbol"], "change_24h": c["price_change_percentage_24h"]} for c in top_gainers
        ],
        "top_losers": [
            {"name": c["name"], "symbol": c["symbol"], "change_24h": c["price_change_percentage_24h"]} for c in top_losers
        ],
        "highest_volume": {
            "name": highest_volume["name"],
            "symbol": highest_volume["symbol"],
            "volume_usd": highest_volume["total_volume"],
        },
    }


def print_results_table(results: dict):
    console.print()
    console.print("[bold cyan]📊 КРИПТО-АНАЛИЗАТОР[/bold cyan]")
    console.print(f"[dim]Отчёт сгенерирован: {results['generated_at']}[/dim]")
    console.print(f"[dim]Проанализировано монет: {results['total_coins_analyzed']}[/dim]")
    console.print(f"[dim]Общая капитализация: ${results['total_market_cap_usd']:,.0f}[/dim]")
    console.print()
    gainers_table = Table(title="🚀 Топ-3 лидера роста (24ч)", style="green")
    gainers_table.add_column("Монета", style="bold")
    gainers_table.add_column("Символ", style="dim")
    gainers_table.add_column("Изменение", justify="right")
    for coin in results["top_gainers"]:
        gainers_table.add_row(coin["name"], coin["symbol"].upper(), f"+{coin['change_24h']:.2f}%")
    console.print(gainers_table)
    console.print()
    losers_table = Table(title="📉 Топ-3 лидера падения (24ч)", style="red")
    losers_table.add_column("Монета", style="bold")
    losers_table.add_column("Символ", style="dim")
    losers_table.add_column("Изменение", justify="right")
    for coin in results["top_losers"]:
        losers_table.add_row(coin["name"], coin["symbol"].upper(), f"{coin['change_24h']:.2f}%")
    console.print(losers_table)
    console.print()
    vol = results["highest_volume"]
    console.print(
        f"[bold]🔥 Максимальный объём торгов:[/bold] {vol['name']} ({vol['symbol'].upper()}) — ${vol['volume_usd']:,.0f}"
    )


def save_report(results: dict, filename: str = "crypto_report.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    console.print(f"[green]✅ Отчёт сохранён в {filename}[/green]")


def main():
    console.print("[bold]Загружаю данные с CoinGecko API...[/bold]")
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        task = progress.add_task("Загрузка...", total=None)
        data = fetch_crypto_data()
        progress.update(task, completed=100)
    console.print("[green]✅ Данные загружены![/green]")
    results = analyze_data(data)
    print_results_table(results)
    save_report(results)


def test_retry():
    console.print()
    console.print("[bold yellow]🧪 ТЕСТ ДЕКОРАТОРА @retry[/bold yellow]")
    console.print("[dim]Пробуем загрузить данные со сломанного URL...[/dim]")
    console.print()
    try:
        fetch_crypto_data(url="https://BROKEN-URL-TEST-12345.com/api")
    except requests.RequestException as e:
        console.print(f"[red]❌ Все попытки исчерпаны. Ошибка: {type(e).__name__}[/red]")
        console.print("[green]✅ Декоратор @retry отработал корректно![/green]")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test-retry":
        test_retry()
    else:
        main()
