# -*- coding: UTF-8 -*-
"""
Create a runner as behave plugin by using its name:

* scoped-class-name, like: "behave.runner:Runner" (dotted.module:ClassName)
* runner-alias (alias mapping provided in config-file "behave.runners" section)

.. code-block:: ini

    # -- FILE: behave.ini
    # RUNNER-ALIAS EXAMPLE:
    # USE: behave --runner=default features/
    [behave.runners]
    default = behave.runner:Runner
"""

from __future__ import absolute_import, print_function
import inspect
from behave.api.runner import ITestRunner
from behave.exception import (
    ConfigError,
    ClassNotFoundError,
    InvalidClassError,
    # MAYBE: ModuleNotFoundError
)
from behave.importer import load_module, make_scoped_class_name, parse_scoped_name
from behave._types import Unknown


class RunnerPlugin(object):
    """Extension point to load a runner_class and create its runner:

    * create a runner by using its scoped-class-name
    * create a runner by using its runner-alias (provided in config-file)
    * create a runner by using a runner-class

    .. code-block:: python

        # -- EXAMPLE: Provide own test runner-class
        from behave.api.runner import ITestRunner

        class MyRunner(ITestRunner):
            def __init__(self, config, **kwargs):
                self.config = config

            def run(self):
                ... # IMPLEMENTATION DETAILS: Left out here.

    .. code-block:: python

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
        if not runner_class and runner_name and inspect.isclass(runner_name):
            # -- USABILITY: Use runner_name as runner_class
            runner_class = runner_name
            runner_name = make_scoped_class_name(runner_class)
        self.runner_name = runner_name
        self.runner_class = runner_class
        self.runner_aliases = runner_aliases or {}

    @staticmethod
    def is_class_valid(runner_class):
        run_method = getattr(runner_class, "run", None)
        return (inspect.isclass(runner_class) and
                issubclass(runner_class, ITestRunner) and
                callable(run_method))

    @staticmethod
    def validate_class(runner_class, runner_class_name=None):
        """Check if a runner class supports the Runner API constraints."""
        if not runner_class_name:
            runner_class_name = make_scoped_class_name(runner_class)

        if not inspect.isclass(runner_class):
            raise InvalidClassError("is not a class")
        elif not issubclass(runner_class, ITestRunner):
            message = "is not a subclass-of 'behave.api.runner:ITestRunner'"
            raise InvalidClassError(message)

        run_method = getattr(runner_class, "run", None)
        if not callable(run_method):
            raise InvalidClassError("run() is not callable")

        undefined_steps = getattr(runner_class, "undefined_steps", None)
        if undefined_steps is None:
            raise InvalidClassError("undefined_steps: missing attribute or property")
        # MAYBE:
        # elif not callable(undefined_steps):
        #     raise InvalidClassError("undefined_steps is not callable")

    @classmethod
    def load_class(cls, runner_class_name, verbose=True):
        """Loads a runner class by using its scoped-class-name, like:
        `my.module:Class1`.

        :param runner_class_name:  Scoped class-name (as string).
        :return: Loaded runner-class (on success).
        :raises ModleNotFoundError: If module does not exist or not importable.
        :raises ClassNotFoundError: If module exist, but class was not found.
        :raises InvalidClassError: If class is invalid (wrong subclass or not a class).
        :raises ImportError: If module was not found (or other Import-Errors above).
        """
        module_name, class_name = parse_scoped_name(runner_class_name)
        try:
            module = load_module(module_name)
            runner_class = getattr(module, class_name, Unknown)
            if runner_class is Unknown:
                raise ClassNotFoundError(runner_class_name)
            cls.validate_class(runner_class, runner_class_name)
            return runner_class
        except (ImportError, InvalidClassError, TypeError) as e:
            # -- CASE: ModuleNotFoundError, ClassNotFoundError, InvalidClassError, ...
            if verbose:
                print("BAD_RUNNER_CLASS: FAILED to load runner.class=%s (%s)" % \
                      (runner_class_name, e.__class__.__name__))
            raise

    @classmethod
    def make_problem_description(cls, scoped_class_name, use_details=False):
        """Check runner class for problems.

        :param scoped_class_name:  Runner class name (as string).
        :return: EMPTY_STRING, if no problem exists.
        :return: Problem exception class name (as string).
        """
        # -- STEP: Check runner for problems
        problem_description = ""
        try:
            cls.load_class(scoped_class_name, verbose=False)
        except (ImportError, TypeError) as e:
            problem_description = e.__class__.__name__
            if use_details:
                problem_description = "%s: %s" % (problem_description, str(e))
        return problem_description

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
            runner_name = self.runner_name or config.runner
            runner_aliases = {}
            runner_aliases.update(config.runner_aliases)
            runner_aliases.update(self.runner_aliases)
            scoped_class_name = runner_aliases.get(runner_name, runner_name)
            if scoped_class_name == runner_name and ":" not in scoped_class_name:
                # -- CASE: runner-alias is not in config-file section="behave.runner".
                raise ConfigError("runner=%s (RUNNER-ALIAS NOT FOUND)" % scoped_class_name)
            runner_class = self.load_class(scoped_class_name)
        else:
            self.validate_class(runner_class)

        runner = runner_class(config, **runner_kwargs)
        return runner
