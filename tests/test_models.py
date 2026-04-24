import pytest
from models.crypto_asset import CryptoAsset


class TestCryptoAssetValidation:
    """Тесты валидации."""

    def test_empty_name_raises_error(self):
        with pytest.raises(ValueError, match="name"):
            CryptoAsset("", "BTC", 100.0, 1.0)

    def test_empty_symbol_raises_error(self):
        with pytest.raises(ValueError, match="symbol"):
            CryptoAsset("Bitcoin", "", 100.0, 1.0)

    def test_invalid_price_type_raises_error(self):
        with pytest.raises(TypeError, match="price"):
            CryptoAsset("Bitcoin", "BTC", "invalid", 1.0)

    def test_invalid_change_type_raises_error(self):
        with pytest.raises(TypeError, match="change_24h"):
            CryptoAsset("Bitcoin", "BTC", 100.0, "invalid")

    @pytest.mark.parametrize("name,symbol,price,change", [
        ("Bitcoin", "BTC", 50000.0, 2.5),
        ("Ethereum", "ETH", 3000.0, -1.2),
        ("X", "X", 0.0001, 999.9),
    ])
    def test_valid_data_passes(self, name, symbol, price, change):
        asset = CryptoAsset(name, symbol, price, change)
        assert asset.name == name


class TestCryptoAssetMagicMethods:
    """Тесты магических методов."""

    def test_str(self, sample_asset):
        result = str(sample_asset)
        assert "Bitcoin" in result
        assert "50000.00" in result

    def test_repr(self, sample_asset):
        result = repr(sample_asset)
        assert "CryptoAsset(" in result

    def test_lt_true(self):
        a = CryptoAsset("A", "A", 10, 1.0)
        b = CryptoAsset("B", "B", 10, 2.0)
        assert a < b

    def test_gt_true(self):
        a = CryptoAsset("A", "A", 10, 2.0)
        b = CryptoAsset("B", "B", 10, 1.0)
        assert a > b

    def test_lt_not_implemented(self, sample_asset):
        with pytest.raises(TypeError):
            sample_asset < "not an asset"

    def test_lt_equal(self):
    a = CryptoAsset("A", "A", 10, 1.0)
    b = CryptoAsset("B", "B", 10, 1.0)
    assert not a < b
    assert not b < a

    def test_gt_equal(self):
    a = CryptoAsset("A", "A", 10, 1.0)
    b = CryptoAsset("B", "B", 10, 1.0)
    assert not a > b
    assert not b > a

    
class TestCryptoAssetEdgeCases:
    """Граничные случаи."""

    def test_negative_price(self):
        asset = CryptoAsset("T", "T", -100.0, 0.0)
        assert asset.price == -100.0

    def test_unicode_name(self):
        asset = CryptoAsset("ビットコイン", "BTC", 100.0, 0.0)
        assert asset.name == "ビットコイン"

    def test_special_symbol(self):
        asset = CryptoAsset("T", "BTC-USD", 100.0, 0.0)
        assert asset.symbol == "BTC-USD"


