from formatters.factory import FormatterFactory
from formatters.console import ConsoleFormatter
from formatters.json import JSONFormatter
from formatters.csv import CSVFormatter

FormatterFactory.register("console", ConsoleFormatter)
FormatterFactory.register("json", JSONFormatter)
FormatterFactory.register("csv", CSVFormatter)