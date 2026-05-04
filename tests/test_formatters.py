import json
import pytest
from unittest.mock import patch, Mock

from formatters.console import ConsoleFormatter
from formatters.json import JSONFormatter
from formatters.csv import CSVFormatter
from formatters.base import OutputFormatter
from formatters.factory import FormatterFactory


class TestConsoleFormatter:
    def test_inherits_from_base(self):
        assert isinstance(ConsoleFormatter(), OutputFormatter)

    def test_format_prints(self, sample_assets_list):
        formatter = ConsoleFormatter()
        with patch("rich.console.Console.print") as mock_print:
            formatter.format(sample_assets_list[:2], sample_assets_list[2:])
            assert mock_print.called

    def test_format_empty(self):
        formatter = ConsoleFormatter()
        with patch("rich.console.Console.print") as mock_print:
            formatter.format([], [])
            assert mock_print.called


class TestJSONFormatter:
    def test_inherits_from_base(self):
        assert isinstance(JSONFormatter(), OutputFormatter)

    def test_format_outputs_valid_json(self, sample_assets_list):
        formatter = JSONFormatter()
        with patch("builtins.print") as mock_print:
            formatter.format(sample_assets_list[:2], sample_assets_list[2:])
            output = mock_print.call_args[0][0]
            data = json.loads(output)
            assert "top_gainers" in data
            assert "top_losers" in data

    def test_format_empty(self):
        formatter = JSONFormatter()
        with patch("builtins.print") as mock_print:
            formatter.format([], [])
            output = mock_print.call_args[0][0]
            data = json.loads(output)
            assert data == {"top_gainers": [], "top_losers": []}


class TestCSVFormatter:
    def test_inherits_from_base(self):
        assert isinstance(CSVFormatter(), OutputFormatter)

    def test_format_writes_csv(self, sample_assets_list):
        formatter = CSVFormatter()
        with patch("csv.writer") as mock_writer:
            mock_writer_instance = Mock()
            mock_writer.return_value = mock_writer_instance
            formatter.format(sample_assets_list[:2], sample_assets_list[2:])
            assert mock_writer.called

    def test_format_empty(self):
        formatter = CSVFormatter()
        with patch("csv.writer") as mock_writer:
            mock_writer_instance = Mock()
            mock_writer.return_value = mock_writer_instance
            formatter.format([], [])
            assert mock_writer_instance.writerow.call_count >= 1


class TestFormatterFactory:
    @pytest.mark.parametrize("name,expected_class", [
        ("console", ConsoleFormatter),
        ("json", JSONFormatter),
        ("csv", CSVFormatter),
    ])
    def test_create(self, name, expected_class):
        formatter = FormatterFactory.create(name)
        assert isinstance(formatter, expected_class)

    def test_unknown_formatter(self):
        with pytest.raises(ValueError, match="Unknown formatter"):
            FormatterFactory.create("xml")


class TestFormatterPolymorphism:
    def test_all_implement_format(self):
        for name in ["console", "json", "csv"]:
            formatter = FormatterFactory.create(name)
            assert hasattr(formatter, "format")
            assert callable(formatter.format)