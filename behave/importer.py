# -*- coding: utf-8 -*-
"""
Importer module for lazy-loading/importing modules and objects.

REQUIRES: importlib (provided in Python2.7, Python3.2...)
"""

try:
    import importlib
except ImportError:
    raise SystemExit("REQUIRES: importlib (or backport)")


class Unknown(object):
    pass

class LazyObject(object):
    def __init__(self, module_name, object_name=None):
        if ":" in module_name and not object_name:
            module_name, object_name = module_name.split(":")
        assert ":" not in module_name
        self.module_name = module_name
        self.object_name = object_name
        self._module = None
        self._object = None

    @staticmethod
    def load_module(module_name):
        return importlib.import_module(module_name)

    def get(self):
        if self._object:
            return self._object

        # -- NORMAL CASE:
        if not self._module:
            self._module = self.load_module(self.module_name)
        obj = getattr(self._module, self.object_name, Unknown)
        if obj is Unknown:
            msg = "%s: %s is Unknown" % (self.module_name, self.object_name)
            raise ImportError(msg)
        self._object = obj
        return obj


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
        value = self.get(key, Unknown)
        if value is Unknown:
            raise KeyError(key)
        elif isinstance(value, LazyObject):
            value = value.get()
            self[key] = value
        return value