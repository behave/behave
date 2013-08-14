# -*- coding: utf-8 -*-
"""
Importer module for lazy-loading/importing modules and objects.

REQUIRES: importlib (provided in Python2.7, Python3.2...)
"""

from behave.compat import importlib


class Unknown(object):
    pass


class LazyObject(object):
    """
    Provides a placeholder for an object that should be loaded lazily.
    """

    def __init__(self, module_name, object_name=None):
        if ":" in module_name and not object_name:
            module_name, object_name = module_name.split(":")
        assert ":" not in module_name
        self.module_name = module_name
        self.object_name = object_name
        self.obj = None

    @staticmethod
    def load_module(module_name):
        return importlib.import_module(module_name)

    def __get__(self, obj=None, type=None):
        """
        Implement descriptor protocol,
        useful if this class is used as attribute.
        :return: Real object (lazy-loaded if necessary).
        :raise ImportError: If module or object cannot be imported.
        """
        __pychecker__ = "unusednames=obj,type"
        if not self.obj:
            # -- SETUP-ONCE: Lazy load the real object.
            module = self.load_module(self.module_name)
            obj = getattr(module, self.object_name, Unknown)
            if obj is Unknown:
                msg = "%s: %s is Unknown" % (self.module_name, self.object_name)
                raise ImportError(msg)
            self.obj = obj
        return obj

    def __set__(self, obj, value):
        """
        Implement descriptor protocol.
        """
        __pychecker__ = "unusednames=obj"
        self.obj = value

    def get(self):
        return self.__get__()


class LazyDict(dict):
    """
    Provides a dict that supports lazy loading of objects.
    A LazyObject is provided as placeholder for a value that should be
    loaded lazily.
    """

    def __getitem__(self, key):
        """
        Provides access to stored dict values.
        Implements lazy loading of item value (if necessary).
        When lazy object is loaded, its value with the dict is replaced
        with the real value.

        :param key:  Key to access the value of an item in the dict.
        :return: value
        :raises: KeyError if item is not found
        :raises: ImportError for a LazyObject that cannot be imported.
        """
        value = dict.__getitem__(self, key)
        if isinstance(value, LazyObject):
            # -- LAZY-LOADING MECHANISM: Load object and replace with lazy one.
            value = value.__get__()
            self[key] = value
        return value
