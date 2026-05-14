from unittest.mock import Mock, patch

import pytest

from decorators import retry


class TestRetryDecorator:
    """Тесты декоратора @retry."""

    def test_success_first_attempt(self):
        mock_func = Mock(return_value="ok")

        @retry(max_attempts=3, delay=0.1)
        def test_func():
            return mock_func()

        result = test_func()
        assert result == "ok"
        assert mock_func.call_count == 1

    def test_success_after_failures(self):
        mock_func = Mock(side_effect=[ValueError, ValueError, "ok"])

        @retry(max_attempts=3, delay=0.1)
        def test_func():
            return mock_func()

        with patch("time.sleep"):
            result = test_func()

        assert result == "ok"
        assert mock_func.call_count == 3

    def test_all_attempts_fail(self):
        mock_func = Mock(side_effect=ValueError("error"))

        @retry(max_attempts=3, delay=0.1)
        def test_func():
            return mock_func()

        with patch("time.sleep"):
            with pytest.raises(ValueError, match="error"):
                test_func()

        assert mock_func.call_count == 3

    @pytest.mark.parametrize("max_attempts", [1, 2, 5])
    def test_max_attempts_respected(self, max_attempts):
        mock_func = Mock(side_effect=ValueError)

        @retry(max_attempts=max_attempts, delay=0.01)
        def test_func():
            return mock_func()

        with patch("time.sleep"):
            with pytest.raises(ValueError):
                test_func()

        assert mock_func.call_count == max_attempts

    def test_preserves_metadata(self):
        @retry(max_attempts=3)
        def my_func():
            """Docstring."""
            pass

        assert my_func.__name__ == "my_func"
        assert my_func.__doc__ == "Docstring."
