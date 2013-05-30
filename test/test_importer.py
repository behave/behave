# -*- coding: utf-8 -*-
"""
Tests for behave.importing.
The module provides a lazy-loading/importing mechanism.
"""

from behave.importer import LazyObject, LazyDict
from behave.formatter.base import Formatter
from nose.tools import eq_, assert_raises
import sys
import types
# import unittest


class TestTheory(object): pass
class ImportModuleTheory(TestTheory):
    """
    Provides a test theory for importing modules.
    """

    @classmethod
    def ensure_module_is_not_imported(cls, module_name):
        if module_name in sys.modules:
            del sys.modules[module_name]
        cls.assert_module_is_not_imported(module_name)

    @staticmethod
    def assert_module_is_imported(module_name):
        module = sys.modules.get(module_name, None)
        assert module_name in sys.modules
        assert module is not None

    @staticmethod
    def assert_module_is_not_imported(module_name):
        assert module_name not in sys.modules

    @staticmethod
    def assert_module_with_name(module, name):
        assert isinstance(module, types.ModuleType)
        eq_(module.__name__, name)


class TestLazyObject(object):
    theory = ImportModuleTheory

    def test_load_module__should_fail_for_unknown_module(self):
        assert_raises(ImportError, LazyObject.load_module, "__unknown_module__")

    def test_load_module__should_succeed_for_already_imported_module(self):
        module_name = "behave.importer"
        self.theory.assert_module_is_imported(module_name)

        module = LazyObject.load_module(module_name)
        self.theory.assert_module_with_name(module, module_name)
        self.theory.assert_module_is_imported(module_name)

    def test_load_module__should_succeed_for_existing_module(self):
        module_name = "behave.textutil"
        self.theory.ensure_module_is_not_imported(module_name)

        module = LazyObject.load_module(module_name)
        self.theory.assert_module_with_name(module, module_name)
        self.theory.assert_module_is_imported(module_name)

    def test_get__should_succeed_for_known_object(self):
        lazy = LazyObject("behave.importer", "LazyObject")
        value = lazy.get()
        assert value is LazyObject

        lazy2 = LazyObject("behave.importer:LazyObject")
        value2 = lazy2.get()
        assert value2 is LazyObject

        lazy3 = LazyObject("behave.formatter.steps", "StepsFormatter")
        value3 = lazy3.get()
        assert issubclass(value3, Formatter)

    def test_get__should_fail_for_unknown_module(self):
        lazy = LazyObject("__unknown_module__", "xxx")
        assert_raises(ImportError, lazy.get)

    def test_get__should_fail_for_unknown_object_in_module(self):
        lazy = LazyObject("behave.textutil", "xxx")
        assert_raises(ImportError, lazy.get)


class LazyDictTheory(TestTheory):

    @staticmethod
    def safe_getitem(data, key):
        return dict.__getitem__(data, key)

    @classmethod
    def assert_item_is_lazy(cls, data, key):
        value = cls.safe_getitem(data, key)
        cls.assert_is_lazy_object(value)

    @classmethod
    def assert_item_is_not_lazy(cls, data, key):
        value = cls.safe_getitem(data, key)
        cls.assert_is_not_lazy_object(value)

    @staticmethod
    def assert_is_lazy_object(obj):
        assert isinstance(obj, LazyObject)

    @staticmethod
    def assert_is_not_lazy_object(obj):
        assert not isinstance(obj, LazyObject)


class TestLazyDict(object):
    theory = LazyDictTheory

    def test_unknown_item_access__should_raise_keyerror(self):
        lazy_dict = LazyDict({"alice": 42})
        item_access = lambda key: lazy_dict[key]
        assert_raises(KeyError, item_access, "unknown")

    def test_plain_item_access__should_succeed(self):
        theory = LazyDictTheory
        lazy_dict = LazyDict({"alice": 42})
        theory.assert_item_is_not_lazy(lazy_dict, "alice")

        value = lazy_dict["alice"]
        eq_(value, 42)

    def test_lazy_item_access__should_load_object(self):
        ImportModuleTheory.ensure_module_is_not_imported("inspect")
        lazy_dict = LazyDict({"alice": LazyObject("inspect:ismodule")})
        self.theory.assert_item_is_lazy(lazy_dict, "alice")
        self.theory.assert_item_is_lazy(lazy_dict, "alice")

        value = lazy_dict["alice"]
        self.theory.assert_is_not_lazy_object(value)
        self.theory.assert_item_is_not_lazy(lazy_dict, "alice")

    def test_lazy_item_access__should_fail_with_unknown_module(self):
        lazy_dict = LazyDict({"bob": LazyObject("__unknown_module__", "xxx")})
        item_access = lambda key: lazy_dict[key]
        assert_raises(ImportError, item_access, "bob")

    def test_lazy_item_access__should_fail_with_unknown_object(self):
        lazy_dict = LazyDict({
            "bob": LazyObject("behave.importer", "XUnknown")
        })
        item_access = lambda key: lazy_dict[key]
        assert_raises(ImportError, item_access, "bob")
