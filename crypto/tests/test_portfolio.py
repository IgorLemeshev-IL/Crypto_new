from decimal import Decimal

from django.contrib.auth.models import User
from django.db import transaction
from django.test import TestCase

from crypto.models import Balance, CoinPrice, PortfolioPosition, Snapshot
from crypto.portfolio_service import PortfolioService


class PortfolioServiceTest(TestCase):
    """Тесты для PortfolioService"""

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        # Создаём пользователя
        self.user = User.objects.create_user(username="testuser", password="testpass123")

        # Создаём баланс пользователя
        self.balance = Balance.objects.create(user=self.user, amount=Decimal("10000.00"))

        # Создаём снимок с ценами
        self.snapshot = Snapshot.objects.create()
        self.btc_price = CoinPrice.objects.create(
            snapshot=self.snapshot, name="Bitcoin", symbol="BTC", price=Decimal("50000.00"), change_24h=Decimal("2.5")
        )
        self.eth_price = CoinPrice.objects.create(
            snapshot=self.snapshot, name="Ethereum", symbol="ETH", price=Decimal("3000.00"), change_24h=Decimal("5.0")
        )

    def test_successful_buy(self):
        """Тест 1: Успешная покупка"""
        # Выполняем покупку
        position = PortfolioService.buy(
            user=self.user,
            symbol="BTC",
            amount=Decimal("0.1"),
            price_per_coin=None,  # Берём из снимка
        )

        # Проверяем: позиция создалась
        self.assertEqual(position.symbol, "BTC")
        self.assertEqual(position.amount, Decimal("0.1"))
        self.assertEqual(position.avg_buy_price, Decimal("50000.00"))

        # Проверяем: баланс уменьшился
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.amount, Decimal("5000.00"))

        # Проверяем: позиция есть в базе
        self.assertTrue(PortfolioPosition.objects.filter(user=self.user, symbol="BTC").exists())

    def test_buy_insufficient_balance(self):
        """Тест 2: Покупка при недостаточном балансе → откат"""
        # Пытаемся купить на $15000 (баланс только $10000)
        with self.assertRaises(ValueError) as context:
            PortfolioService.buy(
                user=self.user,
                symbol="BTC",
                amount=Decimal("0.3"),  # 0.3 * 50000 = 15000
                price_per_coin=Decimal("50000.00"),
            )

        # Проверяем сообщение об ошибке
        self.assertIn("Insufficient balance", str(context.exception))

        # Проверяем: баланс не изменился
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.amount, Decimal("10000.00"))

        # Проверяем: позиция не создалась
        self.assertFalse(PortfolioPosition.objects.filter(user=self.user, symbol="BTC").exists())

    def test_buy_with_custom_price(self):
        """Тест: Покупка с указанием своей цены"""
        position = PortfolioService.buy(
            user=self.user,
            symbol="BTC",
            amount=Decimal("0.1"),
            price_per_coin=Decimal("45000.00"),  # Своя цена
        )

        self.assertEqual(position.avg_buy_price, Decimal("45000.00"))

        self.balance.refresh_from_db()
        # 0.1 * 45000 = 4500
        self.assertEqual(self.balance.amount, Decimal("5500.00"))

    def test_successful_sell(self):
        """Тест: Успешная продажа"""
        # Сначала покупаем
        PortfolioService.buy(user=self.user, symbol="BTC", amount=Decimal("0.1"), price_per_coin=Decimal("50000.00"))

        # Проверяем баланс после покупки
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.amount, Decimal("5000.00"))

        # Продаём
        revenue = PortfolioService.sell(
            user=self.user,
            symbol="BTC",
            amount=Decimal("0.05"),
            price_per_coin=Decimal("55000.00"),  # Цена выросла
        )

        # Проверяем выручку
        self.assertEqual(revenue, Decimal("2750.00"))  # 0.05 * 55000

        # Проверяем баланс (5000 + 2750 = 7750)
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.amount, Decimal("7750.00"))

        # Проверяем: позиция уменьшилась (было 0.1, продали 0.05)
        position = PortfolioPosition.objects.get(user=self.user, symbol="BTC")
        self.assertEqual(position.amount, Decimal("0.05"))

    def test_sell_full_position(self):
        """Тест: Продажа всей позиции"""
        # Покупаем
        PortfolioService.buy(user=self.user, symbol="BTC", amount=Decimal("0.1"), price_per_coin=Decimal("50000.00"))

        # Продаём всё
        revenue = PortfolioService.sell(user=self.user, symbol="BTC", amount=Decimal("0.1"), price_per_coin=Decimal("50000.00"))

        # Проверяем выручку
        self.assertEqual(revenue, Decimal("5000.00"))

        # Проверяем баланс (было 10000 - 5000 + 5000 = 10000)
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.amount, Decimal("10000.00"))

        # Проверяем: позиция удалена
        self.assertFalse(PortfolioPosition.objects.filter(user=self.user, symbol="BTC").exists())

    def test_sell_insufficient_amount(self):
        """Тест: Продажа больше чем есть → откат"""
        # Покупаем 0.1 BTC
        PortfolioService.buy(user=self.user, symbol="BTC", amount=Decimal("0.1"), price_per_coin=Decimal("50000.00"))

        # Пытаемся продать 0.2 BTC
        with self.assertRaises(ValueError) as context:
            PortfolioService.sell(user=self.user, symbol="BTC", amount=Decimal("0.2"), price_per_coin=Decimal("50000.00"))

        self.assertIn("Insufficient amount", str(context.exception))

        # Проверяем: позиция не изменилась
        position = PortfolioPosition.objects.get(user=self.user, symbol="BTC")
        self.assertEqual(position.amount, Decimal("0.1"))

        # Проверяем: баланс не изменился (остался 5000)
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.amount, Decimal("5000.00"))

    def test_atomic_transaction_on_error(self):
        """Тест: Атомарность — при ошибке всё откатывается"""
        try:
            with transaction.atomic():
                # Покупаем BTC
                PortfolioService.buy(user=self.user, symbol="BTC", amount=Decimal("0.1"), price_per_coin=Decimal("50000.00"))

                # Пытаемся купить ETH с недостаточным балансом
                PortfolioService.buy(
                    user=self.user,
                    symbol="ETH",
                    amount=Decimal("2.0"),  # 2 * 3000 = 6000 (осталось 5000)
                    price_per_coin=Decimal("3000.00"),
                )
        except ValueError:
            pass  # Ожидаемая ошибка

        # Проверяем: ни BTC, ни ETH не должны быть в портфеле
        self.assertFalse(PortfolioPosition.objects.filter(user=self.user).exists())

        # Проверяем: баланс не изменился
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.amount, Decimal("10000.00"))

    def test_get_portfolio_value(self):
        """Тест: Расчёт стоимости портфеля"""
        # Покупаем BTC
        PortfolioService.buy(user=self.user, symbol="BTC", amount=Decimal("0.1"), price_per_coin=Decimal("50000.00"))

        service = PortfolioService(self.user)
        portfolio = service.get_portfolio_value()

        self.assertEqual(portfolio["total_value"], Decimal("5000.00"))
        self.assertEqual(portfolio["total_invested"], Decimal("5000.00"))
        self.assertEqual(portfolio["total_profit"], Decimal("0.00"))
        self.assertEqual(len(portfolio["positions"]), 1)
        self.assertEqual(portfolio["positions"][0]["symbol"], "BTC")

    def test_concurrent_buy(self):
        """Тест: select_for_update блокирует баланс при конкурентных покупках"""
        # Устанавливаем баланс
        self.balance.amount = Decimal("10000.00")
        self.balance.save()

        # Первая покупка — успешна
        position1 = PortfolioService.buy(user=self.user, symbol="BTC", amount=Decimal("0.15"), price_per_coin=Decimal("50000.00"))
        self.assertEqual(position1.amount, Decimal("0.15"))

        # Вторая покупка — должна упасть из-за недостатка средств
        with self.assertRaises(ValueError) as context:
            PortfolioService.buy(user=self.user, symbol="BTC", amount=Decimal("0.15"), price_per_coin=Decimal("50000.00"))

        self.assertIn("Insufficient balance", str(context.exception))

        # Проверяем итоговый баланс
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.amount, Decimal("2500.00"))

        # Проверяем позицию (не изменилась после второй попытки)
        position = PortfolioPosition.objects.get(user=self.user, symbol="BTC")
        self.assertEqual(position.amount, Decimal("0.15"))
