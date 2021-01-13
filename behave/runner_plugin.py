# -*- coding: UTF-8 -*-
"""
Create a runner as behave plugin by using its name:

* scoped-class-name, like: "behave.runner:Runner" (dotted.module:ClassName)
* runner-alias (alias mapping provided in config-file "behave.runners" section)

.. code-block::

    # -- FILE: behave.ini
    # RUNNER-ALIAS EXAMPLE:
    # USE: behave --runner=default features/
    [behave.runners]
    default = behave.runner:Runner
"""

from __future__ import absolute_import, print_function
import inspect
from behave.api.runner import IRunner
from behave.exception import ConfigError, ClassNotFoundError, InvalidClassError
from behave.importer import parse_scoped_name
from behave._types import Unknown
from importlib import import_module


class RunnerPlugin(object):
    """Extension point to load an runner_class and create its runner:

    * create a runner by using its scoped-class-name
    * create a runner by using its runner-alias (provided in config-file)
    * create a runner by using a runner-class

    .. code-block:: py

        # -- EXAMPLE: Provide own test runner-class
        from behave.api.runner import IRunner
        class MyRunner(IRunner):
            def __init__(self, config, **kwargs):
                self.config = config

            def run(self):
                ... # IMPLEMENTATION DETAILS: Left out here.

    .. code-block:: py

        # -- CASE 1A: Make a runner by using its scoped-class-name
        plugin = RunnerPlugin("behave.runner:Runner")
        runner = plugin.make_runner(config)

        # -- CASE 1B: Make a runner by using its runner-alias
        # CONFIG-FILE SECTION: "behave.ini"
        #   [behave.runners]
        #   one = behave.runner:Runner
        plugin = RunnerPlugin("one")
        runner = plugin.make_runner(config)

        # -- CASE 2: Make a runner by using a runner-class
        from behave.runner import Runner as DefaultRunner
        plugin = RunnerPlugin(runner_class=DefaultRunner)
        runner = plugin.make_runner(config)
    """
    def __init__(self, runner_name=None, runner_class=None, runner_aliases=None):
        self.runner_name = runner_name
        self.runner_class = runner_class
        self.runner_aliases = runner_aliases

    @staticmethod
    def is_runner_class_valid(runner_class):
        run_method = getattr(runner_class, "run", None)
        return (inspect.isclass(runner_class) and
                issubclass(runner_class, IRunner) and
                callable(run_method))

    @staticmethod
    def load_runner_class(runner_class_name):
        """Loads a runner class by using its scoped-class-name, like:
        `my.module:Class1`.

        :param runner_class_name:  Scoped class-name (as string).
        :return: Loaded runner-class (on success).
        :raises ClassNotFoundError: If module exist, but class was not found.
        :raises InvalidClassError: If class is invalid (wrong subclass or not a class).
        :raises ImportError: If module was not found (or other Import-Errors above).
        """
        module_name, class_name = parse_scoped_name(runner_class_name)
        try:
            module = import_module(module_name)
            runner_class = getattr(module, class_name, Unknown)
            if runner_class is Unknown:
                raise ClassNotFoundError(runner_class_name)
            elif not inspect.isclass(runner_class):
                schema = "{0}: not a class"
                raise InvalidClassError(schema.format(runner_class_name))
            elif not issubclass(runner_class, IRunner):
                schema = "{0}: not subclass-of behave.api.runner.IRunner"
                raise InvalidClassError(schema.format(runner_class_name))
            run_method = getattr(runner_class, "run", None)
            if not callable(run_method):
                schema = "{0}: run() is not callable"
                raise InvalidClassError(schema.format(runner_class_name))
            return runner_class
        except ImportError as e:
            print("FAILED to load runner-class: %s: %s" % (e.__class__.__name__, e))
            raise
        except TypeError as e:
            print("FAILED to load runner-class: %s: %s" % (e.__class__.__name__, e))
            raise

    def make_runner(self, config, **runner_kwargs):
        """Build a runner either by:

        * providing a runner-class
        * using its name (alias-name or scoped-class-name).

        :param config:   Configuration object to use for runner.
        :param runner_kwargs:  Keyword args for runner creation.
        :return: Runner object to use.
        :raises ClassNotFoundError: If module exist, but class was not found.
        :raises InvalidClassError: If class is invalid (wrong subclass or not a class).
        :raises ImportError: If module was not found (or other Import-Errors above).
        :raises ConfigError: If runner-alias is not in config-file (section: behave.runners).
        """
        runner_class = self.runner_class
        if not runner_class:
            # -- CASE: Using runner-name (alias) or scoped_class_name.
            runner_name = self.runner_name
            runner_aliases = self.runner_aliases
            if runner_aliases is None:
                runner_aliases = config.runner_aliases
            if not runner_name:
                runner_name = config.runner
            scoped_class_name = runner_aliases.get(runner_name, runner_name)
            if scoped_class_name == runner_name and ":" not in scoped_class_name:
                # -- CASE: runner-alias is not in config-file section="behave.runner".
                raise ConfigError("runner=%s (RUNNER-ALIAS NOT FOUND)" % scoped_class_name)
            runner_class = self.load_runner_class(scoped_class_name)

        assert self.is_runner_class_valid(runner_class)
        runner = runner_class(config, **runner_kwargs)
        return runner
