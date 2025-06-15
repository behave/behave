# ruff: noqa: F401
"""
* Public API that should be used by formatter classes
* Functionality to register a formatter/formatter-class
"""

# -- FORMATTER INTERFACES and FORMATTER BASE CLASSES:
from behave.formatter.api import IFormatter, IFormatter2
from behave.formatter.base import Formatter, StreamOpener
from behave.formatter.base2 import BaseFormatter2

# -- FORMATTER REGISTRATION FUNCTIONALITY:
from behave.formatter._registry import (
    register as register_formatter,
    register_as as register_formatter_as,
    register_formats
)
