# -*- coding: utf-8 -*-
"""

"""

__author__ = "Jens Engel"

from behave.importer import LazyObject, LazyDict
from behave.formatter.base import Formatter
# from nose.tools import *
import sys
import types
import unittest

class TestTheory(unittest.TestCase):
    def runTest(self, *args, **kwargs):
        pass


class ImportModuleTheory(TestTheory):
    """
    Provides a test theory for importing modules.
    """

    def ensure_module_is_not_imported(self, module_name):
        if module_name in sys.modules:
            del sys.modules[module_name]
        self.assert_module_is_not_imported(module_name)

    def assert_module_is_imported(self, module_name):
        module = sys.modules.get(module_name, None)
        assert module_name in sys.modules
        assert module is not None

    def assert_module_is_not_imported(self, module_name):
        assert module_name not in sys.modules

    def assert_module_with_name(self, module, name):
        assert isinstance(module, types.ModuleType)
        self.assertEqual(module.__name__, name)


class LazyObjectTest(unittest.TestCase):

    def test_load_module__should_fail_for_unknown_module(self):
        self.assertRaises(ImportError, LazyObject.load_module, "__unknown_module__")

    def test_load_module__should_succeed_for_already_imported_module(self):
        theory = ImportModuleTheory()
        module_name = "behave.importer"
        theory.assert_module_is_imported(module_name)

        module = LazyObject.load_module(module_name)
        theory.assert_module_with_name(module, module_name)
        theory.assert_module_is_imported(module_name)

    def test_load_module__should_succeed_for_existing_module(self):
        theory = ImportModuleTheory()
        module_name = "behave.textutil"
        theory.ensure_module_is_not_imported(module_name)

        module = LazyObject.load_module(module_name)
        theory.assert_module_with_name(module, module_name)
        theory.assert_module_is_imported(module_name)


    def test_get__should_succeed_for_known_object(self):
        lazy = LazyObject("behave.importer", "LazyObject")
        value = lazy.get()
        assert value is LazyObject

        lazy2 = LazyObject("behave.importer:LazyObject")
        value2 = lazy2.get()
        assert value2 is LazyObject

        lazy3  = LazyObject("behave.formatter.steps", "StepsFormatter")
        value3 = lazy3.get()
        assert issubclass(value3, Formatter)

    def test_get__should_fail_for_unknown_module(self):
        lazy = LazyObject("__unknown_module__", "xxx")
        self.assertRaises(ImportError, lazy.get)

    def test_get__should_fail_for_unknown_object_in_module(self):
        lazy = LazyObject("behave.textutil", "xxx")
        self.assertRaises(ImportError, lazy.get)

class LazyDictTheory(TestTheory):

    @staticmethod
    def safe_getitem(data, key):
        return dict.__getitem__(data, key)

    def assert_item_is_lazy(self, data, key):
        value = self.safe_getitem(data, key)
        self.assert_is_lazy_object(value)

    def assert_item_is_not_lazy(self, data, key):
        value = self.safe_getitem(data, key)
        self.assert_is_not_lazy_object(value)

    def assert_is_lazy_object(self, obj):
        assert isinstance(obj, LazyObject)

    def assert_is_not_lazy_object(self, obj):
        assert not isinstance(obj, LazyObject)


class LazyDictTest(unittest.TestCase):

    def test_plain_item_access_should_succeed(self):
        theory = LazyDictTheory()
        lazy_dict = LazyDict({"alice": 42})
        theory.assert_item_is_not_lazy(lazy_dict, "alice")

        value = lazy_dict["alice"]
        self.assertEqual(value, 42)

    def test_item_access_should_load_object(self):
        import_theory = ImportModuleTheory()
        import_theory.ensure_module_is_not_imported("inspect")

        theory = LazyDictTheory()
        lazy_dict = LazyDict({"alice": LazyObject("inspect:ismodule")})
        theory.assert_item_is_lazy(lazy_dict, "alice")
        theory.assert_item_is_lazy(lazy_dict, "alice")

        value = lazy_dict["alice"]
        theory.assert_is_not_lazy_object(value)
        theory.assert_item_is_not_lazy(lazy_dict, "alice")

    def test_item_access_should_fail_with_unknown_module(self):
        lazy_dict = LazyDict({"bob": LazyObject("__unknown_module__", "xxx")})
        item_access = lambda key: lazy_dict[key]
        self.assertRaises(ImportError, item_access, "bob")

    def test_item_access_should_fail_with_unknown_object(self):
        lazy_dict = LazyDict({"bob": LazyObject("behave.importer", "XUnknown")})
        item_access = lambda key: lazy_dict[key]
        self.assertRaises(ImportError, item_access, "bob")
