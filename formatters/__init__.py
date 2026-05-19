from formatters.console import ConsoleFormatter
from formatters.csv import CSVFormatter
from formatters.factory import FormatterFactory
from formatters.json import JSONFormatter

FormatterFactory.register("console", ConsoleFormatter)
FormatterFactory.register("json", JSONFormatter)
FormatterFactory.register("csv", CSVFormatter)
