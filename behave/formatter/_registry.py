# -*- coding: utf-8 -*-

from behave.formatter.base import Formatter, StreamOpener
from behave.importer import LazyDict, LazyObject, load_class
import six
import sys
import warnings


# -----------------------------------------------------------------------------
# FORMATTER REGISTRY:
# -----------------------------------------------------------------------------
_formatter_registry = LazyDict()

def format_iter():
    return iter(_formatter_registry.keys())

def format_items(resolved=False):
    if resolved:
        # -- ENSURE: All formatter classes are loaded (and resolved).
        _formatter_registry.load_all(strict=False)
    return iter(_formatter_registry.items())

def register_as(name, formatter_class):
    """
    Register formatter class with given name.

    :param name:  Name for this formatter (as identifier).
    :param formatter_class:  Formatter class to register.

    .. since:: 1.2.5
        Parameter ordering starts with name.
    """
    if not isinstance(name, six.string_types):
        # -- REORDER-PARAMS: Used old ordering before behave-1.2.5 (2015).
        warnings.warn("Use parameter ordering: name, formatter_class (for: %s)" % formatter_class)
        _formatter_class = name
        name = formatter_class
        formatter_class = _formatter_class

    if isinstance(formatter_class, six.string_types):
        # -- SPEEDUP-STARTUP: Only import formatter_class when used.
        scoped_formatter_class_name = formatter_class
        formatter_class = LazyObject(scoped_formatter_class_name)
    assert (isinstance(formatter_class, LazyObject) or
            issubclass(formatter_class, Formatter))
    _formatter_registry[name] = formatter_class

def register(formatter_class):
    register_as(formatter_class.name, formatter_class)

def register_formats(format_items):
    """Register many format items into the registry.

    :param format_items:  List of format items (as: (name, class|class_name)).
    """
    for formatter_name, formatter_class_name in format_items:
        register_as(formatter_name, formatter_class_name)


def select_formatter_class(formatter_name):
    """Resolve the formatter class by:

      * using one of the registered ones
      * loading a user-specified formatter class (like: my.module_name:MyClass)

    :param formatter_name:  Name of the formatter or scoped name (as string).
    :return: Formatter class
    :raises: LookupError, if not found.
    :raises: ImportError, if a user-specific formatter class cannot be loaded.
    :raises: ValueError, if formatter name is invalid.
    """
    try:
        return _formatter_registry[formatter_name]
    except KeyError:
        # -- NOT-FOUND:
        if ":" not in formatter_name:
            raise
        # -- OTHERWISE: SCOPED-NAME, try to load a user-specific formatter.
        # MAY RAISE: ImportError
        return load_class(formatter_name)


def is_formatter_valid(formatter_name):
    """Checks if the formatter is known (registered) or loadable.

    :param formatter_name: Format(ter) name to check (as string).
    :return: True, if formatter is known or can be loaded.
    """
    try:
        formatter_class = select_formatter_class(formatter_name)
        return issubclass(formatter_class, Formatter)
    except (LookupError, ImportError, ValueError):
        return False


def make_formatters(config, stream_openers):
    """Build a list of formatter, used by a behave runner.

    :param config:  Configuration object to use.
    :param stream_openers: List of stream openers to use (for formatters).
    :return: List of formatters.
    :raises: LookupError/KeyError if a formatter class is unknown.
    :raises: ImportError, if a formatter class cannot be loaded/resolved.
    """
    # -- BUILD: Formatter list
    default_stream_opener = StreamOpener(stream=sys.stdout)
    formatter_list = []
    for i, name in enumerate(config.format):
        stream_opener = default_stream_opener
        if i < len(stream_openers):
            stream_opener = stream_openers[i]
        formatter_class = select_formatter_class(name)
        formatter_object = formatter_class(stream_opener, config)
        formatter_list.append(formatter_object)
    return formatter_list
