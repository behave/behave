# -*- coding: utf-8 -*-
"""
Importer module for lazy-loading/importing modules and objects.

REQUIRES: importlib (provided in Python2.7, Python3.2...)
"""

from __future__ import absolute_import
import importlib
import inspect
from behave._types import Unknown
from behave.exception import ClassNotFoundError, ModuleNotFoundError


def parse_scoped_name(scoped_name):
    """
    SCHEMA: my.module_name:MyClassName
    EXAMPLE:
        behave.formatter.plain:PlainFormatter
    """
    scoped_name = scoped_name.strip()
    if "::" in scoped_name:
        # -- ALTERNATIVE: my.module_name::MyClassName
        scoped_name = scoped_name.replace("::", ":")
    if ":" not in scoped_name:
        schema = "%s: Missing ':' (colon) as module-to-name seperator'"
        raise ValueError(schema % scoped_name)
    module_name, object_name = scoped_name.rsplit(":", 1)
    return module_name, object_name or ""


def make_scoped_class_name(obj):
    """Build scoped-class-name from an object/class.

    :param obj:  Object or class.
    :return Scoped-class-name (as string).
    """
    if inspect.isclass(obj):
        class_name = obj.__name__
    else:
        class_name = obj.__class__.__name__
    module_name = getattr(obj, "__module__", None)
    if module_name:
        return "{0}:{1}".format(obj.__module__, class_name)
    # -- OTHERWISE: Builtin data type
    return class_name


def load_module(module_name):
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        # -- SINCE: Python 3.6 (special kind of ImportError)
        raise
    except ImportError as e:
        # -- CASE: Python < 3.6 (Python 2.7, ...)
        msg = str(e)
        if not msg.endswith("'"):
            # -- NOTE: Emulate ModuleNotFoundError message:
            #    "No module named '{module_name}'"
            prefix, module_name = msg.rsplit(" ", 1)
            msg = "{0} '{1}'".format(prefix, module_name)
        raise ModuleNotFoundError(msg)


class LazyObject(object):
    """Provides a placeholder for an class/object that should be loaded lazily.

    It stores the module-name, object-name/class-name and
    imports it later (on demand) when this lazy-object is accessed.
    """

    def __init__(self, module_name, object_name=None):
        if ":" in module_name and not object_name:
            module_name, object_name = parse_scoped_name(module_name)
        assert ":" not in module_name
        self.module_name = module_name
        self.object_name = object_name
        self.resolved_object = None
        self.error = None

    # -- PYTHON DESCRIPTOR PROTOCOL:
    def __get__(self, obj=None, type=None):     # pylint: disable=redefined-builtin
        """Implement descriptor protocol,
        useful if this class is used as attribute.

        :return: Real object (lazy-loaded if necessary).
        :raise ModuleNotFoundError: If module is not found or cannot be imported.
        :raise ClassNotFoundError:  If class/object is not found in module.
        """
        resolved_object = None
        if not self.resolved_object:
            # -- SETUP-ONCE: Lazy load the real object.
            try:
                module = load_module(self.module_name)
                resolved_object = getattr(module, self.object_name, Unknown)
                if resolved_object is Unknown:
                    # OLD: msg = "%s: %s is Unknown" % (self.module_name, self.object_name)
                    scoped_name = "%s:%s" % (self.module_name, self.object_name)
                    raise ClassNotFoundError(scoped_name)
                self.resolved_object = resolved_object
            except ImportError as e:
                self.error = "%s: %s" % (e.__class__.__name__, e)
                raise
                # OR: resolved_object = self
        return resolved_object

    def __set__(self, obj, value):
        """Implement descriptor protocol."""
        self.resolved_object = value

    def get(self):
        return self.__get__()


class LazyDict(dict):
    """Provides a dict that supports lazy loading of classes/objects.
    A LazyObject is provided as placeholder for a value that should be
    loaded lazily.

    EXAMPLE:

    .. code-block:: python

        from behave.importer import LazyDict

        the_plugin_registry = LazyDict({
            "alice": LazyObject("my_module.alice_plugin:AliceClass"),
            "bob": LayzObject("my_module.bob_plugin:BobClass"),
        })

        # -- LATER: Import plugin-class module(s) only if needed.
        # INTENTION: Pay only (with runtime costs) for what you use.
        config.plugin_name = "alice"
        plugin_class = the_plugin_registry[config.plugin_name]
        ...
    """

    def __getitem__(self, key):
        """Provides access to the stored dict value(s).

        Implements lazy loading of item value (if necessary).
        When lazy object is loaded, its value with the dict is replaced
        with the real value.

        :param key:  Key to access the value of an item in the dict.
        :return: value
        :raises KeyError: if item is not found.
        :raises ModuleNotFoundError: for a LazyObject module is not found.
        :raises ClassNotFoundError:  for a LazyObject class/object is not found in module.
        """
        value = dict.__getitem__(self, key)
        if isinstance(value, LazyObject):
            # -- LAZY-LOADING MECHANISM:
            # Load class/object once and replace the lazy placeholder.
            value = value.__get__()
            self[key] = value
        return value

    def load_all(self, strict=False):
        for key in self.keys():
            try:
                self.__getitem__(key)
            except ImportError:
                if strict:
                    raise
