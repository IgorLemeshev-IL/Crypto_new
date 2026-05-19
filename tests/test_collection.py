import pytest

from models.portfolio import CryptoPortfolio


class TestCryptoPortfolio:
    """Тесты коллекции."""

    def test_len(self, sample_assets_list):
        p = CryptoPortfolio(sample_assets_list)
        assert len(p) == 5

    def test_iter(self, sample_assets_list):
        p = CryptoPortfolio(sample_assets_list)
        symbols = [a.symbol for a in p]
        assert symbols == ["BTC", "ETH", "SOL", "ADA", "XRP"]

    def test_getitem(self, sample_assets_list):
        p = CryptoPortfolio(sample_assets_list)
        assert p[0].symbol == "BTC"
        assert p[-1].symbol == "XRP"

    def test_getitem_out_of_range(self, sample_assets_list):
        p = CryptoPortfolio(sample_assets_list)
        with pytest.raises(IndexError):
            p[100]

    def test_top_gainers(self, sample_assets_list):
        p = CryptoPortfolio(sample_assets_list)
        gainers = p.top_gainers(3)
        assert gainers[0].symbol == "SOL"
        assert gainers[1].symbol == "BTC"

    def test_top_losers(self, sample_assets_list):
        p = CryptoPortfolio(sample_assets_list)
        losers = p.top_losers(3)
        assert losers[0].symbol == "ADA"
        assert losers[1].symbol == "ETH"

    def test_filter_positive(self, sample_assets_list):
        p = CryptoPortfolio(sample_assets_list)
        pos = p.filter_positive()
        assert len(pos) == 3

    def test_filter_negative(self, sample_assets_list):
        p = CryptoPortfolio(sample_assets_list)
        neg = p.filter_negative()
        assert len(neg) == 2

    def test_total_value(self, sample_assets_list):
        p = CryptoPortfolio(sample_assets_list)
        assert p.total_value() == 50000.0 + 3000.0 + 100.0 + 0.5 + 0.8

    def test_empty_portfolio(self):
        p = CryptoPortfolio([])
        assert len(p) == 0
        assert p.top_gainers() == []
        assert p.total_value() == 0.0
