# -*- coding: UTF-8 -*-
# pylint: disable=useless-object-inheritance
# pylint: disable=super-with-arguments
"""
This module provides low-level helper functionality during step imports.

.. warn:: Do not use directly

    It should not be used directly except in behave Runner classes
    that need to provide the correct context (step_registry, matchers, etc.)
    instead of using the global module specific variables.
"""

from __future__ import absolute_import
from contextlib import contextmanager
from threading import Lock
from types import ModuleType
import os.path
import sys
import six

from behave import step_registry as _step_registry
from behave.matchers import StepMatcherFactory
from behave.step_registry import StepRegistry


# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def setup_api_with_step_decorators(module, step_registry):
    _step_registry.setup_step_decorators(module, step_registry)


def setup_api_with_matcher_functions(module, step_matcher_factory):
    # -- PUBLIC API: Same as behave.api.step_matchers
    module.use_default_step_matcher = step_matcher_factory.use_default_step_matcher
    module.use_step_matcher = step_matcher_factory.use_step_matcher
    module.step_matcher = step_matcher_factory.use_step_matcher
    module.register_type = step_matcher_factory.register_type


class SimpleStepContainer(object):
    def __init__(self, step_registry=None):
        if step_registry is None:
            step_registry = StepRegistry()
        self.step_matcher_factory = StepMatcherFactory()
        self.step_registry = step_registry
        self.step_registry.step_matcher_factory = self.step_matcher_factory


# -----------------------------------------------------------------------------
# FAKE MODULE CLASSES: For step imports
# -----------------------------------------------------------------------------
# class FakeModule(object):
class FakeModule(ModuleType):
    ensure_fake = True

    # -- SUPPORT FOR: behave.step_registry.setup_step_decorators()
    def __setitem__(self, name, value):
        if "." in name:
            raise ValueError("REQUIRE NOT-DOTTED: name={}".format(name))
        setattr(self, name, value)


class StepRegistryModule(FakeModule):
    """Provides a fake :mod:`behave.step_registry` module
    that can be used during step imports.
    """
    __all__ = [
        "given", "when", "then", "step",
        "Given", "When", "Then", "Step",
    ]

    def __init__(self, step_registry):
        super(StepRegistryModule, self).__init__("behave.step_registry")
        self.registry = step_registry
        setup_api_with_step_decorators(self, step_registry)


class StepMatchersModule(FakeModule):
    __all__ = [
        "use_default_step_matcher",
        "use_step_matcher",
        "register_type"
        # -- DEPRECATING:
        "step_matcher",
    ]

    def __init__(self, step_matcher_factory):
        super(StepMatchersModule, self).__init__("behave.matchers")
        self.step_matcher_factory = step_matcher_factory
        setup_api_with_matcher_functions(self, step_matcher_factory)
        self.make_step_matcher = step_matcher_factory.make_step_matcher
        # -- DEPRECATED-FUNCTION-COMPATIBILITY
        # self.current_matcher = current_matcher or _matchers.current_matcher
        # self.get_matcher = self.make_step_matcher
        # self.matcher_mapping = ...

        # -- INJECT PYTHON PACKAGE META-DATA:
        # REQUIRED-FOR: Non-fake submodule imports (__path__).
        here = os.path.dirname(__file__)
        self.__file__ = os.path.abspath(os.path.join(here, "matchers.py"))
        self.__name__ = "behave.matchers"
        # self.__path__ = [os.path.abspath(here)]


class BehaveModule(FakeModule):
    __all__ = StepRegistryModule.__all__ + StepMatchersModule.__all__

    def __init__(self, step_registry, step_matcher_factory=None):
        if step_matcher_factory is None:
            step_matcher_factory = step_registry.step_step_matcher_factory
        assert step_matcher_factory is not None
        super(BehaveModule, self).__init__("behave")
        setup_api_with_step_decorators(self, step_registry)
        setup_api_with_matcher_functions(self, step_matcher_factory)
        self.use_default_step_matcher = step_matcher_factory.use_default_step_matcher
        assert step_registry.step_matcher_factory == step_matcher_factory

        # -- INJECT PYTHON PACKAGE META-DATA:
        # REQUIRED-FOR: Non-fake submodule imports (__path__).
        here = os.path.dirname(__file__)
        self.__file__ = os.path.abspath(os.path.join(here, "__init__.py"))
        self.__name__ = "behave"
        self.__path__ = [os.path.abspath(here)]
        self.__package__ = None


class StepImportModuleContext(object):

    def __init__(self, step_container):
        self.step_registry = step_container.step_registry
        self.step_matcher_factory = step_container.step_matcher_factory
        assert self.step_registry.step_matcher_factory == self.step_matcher_factory
        self.step_registry.step_matcher_factory = self.step_matcher_factory

        step_registry_module = StepRegistryModule(self.step_registry)
        step_matchers_module = StepMatchersModule(self.step_matcher_factory)
        behave_module = BehaveModule(self.step_registry, self.step_matcher_factory)
        self.modules = {
            "behave": behave_module,
            "behave.matchers": step_matchers_module,
            "behave.step_registry": step_registry_module,
        }
        # self.default_matcher = self.step_matchers_module.current_matcher

    def reset_current_matcher(self):
        self.step_matcher_factory.use_default_step_matcher()


_step_import_lock = Lock()
unknown = object()

@contextmanager
def use_step_import_modules(step_container):
    """
    Redirect any step/type registration to the runner's step-context object
    during step imports by using fake modules (instead of using module-globals).

    This allows that multiple runners can be used without polluting the
    global variables in problematic modules
    (:mod:`behave.step_registry`, mod:`behave.matchers`).

    .. sourcecode:: python

        # -- RUNNER-IMPLEMENTATION:
        def load_step_definitions(self, ...):
            step_container = self.step_container
            with use_step_import_modules(step_container) as import_context:
                # -- USE: Fake modules during step imports
                ...
                import_context.reset_current_matcher()

    :param step_container:
        Step context object with step_registry, step_matcher_factory.
    """
    orig_modules = {}
    import_context = StepImportModuleContext(step_container)
    with _step_import_lock:
        # -- CRITICAL-SECTION (multi-threading protected)
        try:
            # -- SCOPE-GUARD SETUP: Replace original modules with fake ones.
            for module_name, fake_module in six.iteritems(import_context.modules):
                orig_module = sys.modules.get(module_name, unknown)
                orig_modules[module_name] = orig_module
                sys.modules[module_name] = fake_module

            # -- USE: Fake modules for step imports.
            yield import_context
        finally:
            # -- SCOPE-GUARD CLEANUP: Restore original modules.
            for module_name, orig_module in six.iteritems(orig_modules):
                if orig_module is unknown:
                    del sys.modules[module_name]
                else:
                    sys.modules[module_name] = orig_module
