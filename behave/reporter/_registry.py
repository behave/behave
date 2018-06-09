# -*- coding: utf-8 -*-

import sys
import warnings
from behave.formatter.base import StreamOpener
from behave.reporter.base import Reporter
from behave.importer import LazyDict, LazyObject, parse_scoped_name, load_module
import six


# -----------------------------------------------------------------------------
# REPORTER REGISTRY:
# -----------------------------------------------------------------------------
_reporter_registry = LazyDict()


def format_iter():
    return iter(_reporter_registry.keys())


def format_items(resolved=False):
    if resolved:
        # -- ENSURE: All reporter classes are loaded (and resolved).
        _reporter_registry.load_all(strict=False)
    return iter(_reporter_registry.items())


def register_as(name, reporter_class):
    """
    Register reporter class with given name.

    :param name:  Name for this reporter (as identifier).
    :param reporter_class:  Reporter class to register.

    .. since:: 1.2.5
        Parameter ordering starts with name.
    """
    if not isinstance(name, six.string_types):
        # -- REORDER-PARAMS: Used old ordering before behave-1.2.5 (2015).
        warnings.warn("Use parameter ordering: name, formatter_class (for: %s)"\
                      % reporter_class)
        _reporter_class = name
        name = reporter_class
        reporter_class = _reporter_class

    if isinstance(reporter_class, six.string_types):
        # -- SPEEDUP-STARTUP: Only import formatter_class when used.
        scoped_formatter_class_name = reporter_class
        reporter_class = LazyObject(scoped_formatter_class_name)
    assert (isinstance(reporter_class, LazyObject) or
            issubclass(reporter_class, Reporter))
    _reporter_registry[name] = reporter_class


def register(formatter_class):
    register_as(formatter_class.name, formatter_class)


def register_formats(formats):
    """Register many format items into the registry.

    :param formats:  List of format items (as: (name, class|class_name)).
    """
    for formatter_name, formatter_class_name in formats:
        register_as(formatter_name, formatter_class_name)


def load_reporter_class(scoped_class_name):
    """Load a Reporter class by using its scoped class name.

    :param scoped_class_name:  Reporter module and class name (as string).
    :return: Reporter class.
    :raises: ValueError, if scoped_class_name is invalid.
    :raises: ImportError, if module cannot be loaded or class is not in module.
    """
    if ":" not in scoped_class_name:
        message = 'REQUIRE: "module:class", but was: "%s"' % scoped_class_name
        raise ValueError(message)
    module_name, class_name = parse_scoped_name(scoped_class_name)
    reporter_module = load_module(module_name)
    reporter_class = getattr(reporter_module, class_name, None)
    if reporter_class is None:
        raise ImportError("CLASS NOT FOUND: %s" % scoped_class_name)
    return reporter_class


def select_reporter_class(formatter_name):
    """Resolve the reporter class by:

      * using one of the registered ones
      * loading a user-specified reporter class (like: my.module_name:MyClass)

    :param formatter_name:  Name of the reporter or scoped name (as string).
    :return: Reporter class
    :raises: LookupError, if not found.
    :raises: ImportError, if a user-specific reporter class cannot be loaded.
    :raises: ValueError, if reporter name is invalid.
    """
    try:
        return _reporter_registry[formatter_name]
    except KeyError:
        # -- NOT-FOUND:
        if ":" not in formatter_name:
            raise
        # -- OTHERWISE: SCOPED-NAME, try to load a user-specific reporter.
        # MAY RAISE: ImportError
        return load_reporter_class(formatter_name)


def is_formatter_valid(formatter_name):
    """Checks if the reporter is known (registered) or loadable.

    :param formatter_name: Format(ter) name to check (as string).
    :return: True, if reporter is known or can be loaded.
    """
    try:
        formatter_class = select_reporter_class(formatter_name)
        return issubclass(formatter_class, Reporter)
    except (LookupError, ImportError, ValueError):
        return False
