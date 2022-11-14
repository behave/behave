# -*- coding: UTF-8 -*-
"""
Unit tests for :mod:`behave.runner_plugin`.
"""

from __future__ import absolute_import, print_function
from contextlib import contextmanager
import os
from pathlib import Path

from behave import configuration
from behave.api.runner import ITestRunner
from behave.configuration import Configuration
from behave.exception import ClassNotFoundError, InvalidClassError, ModuleNotFoundError
from behave.runner import Runner as DefaultRunnerClass
from behave.runner_plugin import RunnerPlugin

import pytest


# -----------------------------------------------------------------------------
# TEST SUPPORT:
# -----------------------------------------------------------------------------


@contextmanager
def use_directory(directory_path):
    # -- COMPATIBILITY: Use directory-string instead of Path
    initial_directory = str(Path.cwd())
    try:
        os.chdir(str(directory_path))
        yield directory_path
    finally:
        os.chdir(initial_directory)


# -----------------------------------------------------------------------------
# TEST SUPPORT: TEST RUNNER CLASS CANDIDATES -- GOOD EXAMPLES
# -----------------------------------------------------------------------------
class CustomTestRunner(ITestRunner):
    """Custom, dummy runner"""

    def __init__(self, config, **kwargs):
        self.config = config

    def run(self):
        return True     # OOPS: Failed.


class PhoenixTestRunner(ITestRunner):
    def __init__(self, config, **kwargs):
        self.config = config
        self.the_runner = DefaultRunnerClass(config)

    def run(self, features=None):
        return self.the_runner.run(features=features)


class RegisteredTestRunner(object):
    """Not derived from :class:`behave.api.runner:ITestrunner`.
    In this case, you need to register this class to the interface class.
    """

    def __init__(self, config, **kwargs):
        self.config = config

    def run(self):
        return True     # OOPS: Failed.


# -- REQUIRES REGISTRATION WITH INTERFACE:
# Register as subclass of ITestRunner interface-class.
ITestRunner.register(RegisteredTestRunner)


# -----------------------------------------------------------------------------
# TEST SUPPORT: TEST RUNNERS CANDIDATES -- BAD EXAMPLES
# -----------------------------------------------------------------------------
# SYNDEOME: Is not a class, but a boolean value.
INVALID_TEST_RUNNER_CLASS0 = True


class InvalidTestRunnerNotSubclass(object):
    """SYNDROME: Missing ITestRunner.register(InvalidTestRunnerNotSubclass)."""
    def __int__(self, config):
        pass

    def run(self, features=None):
        return True


class InvalidTestRunnerWithoutCtor(ITestRunner):
    """SYNDROME: ctor() method is missing"""
    def run(self, features=None):
        pass


class InvalidTestRunnerWithoutRun(ITestRunner):
    """SYNDROME: run() method is missing"""
    def __init__(self, config, **kwargs):
        self.config = config


# -----------------------------------------------------------------------------
# TEST SUITE:
# -----------------------------------------------------------------------------
class TestRunnerPlugin(object):
    """Test the runner-plugin configuration."""
    THIS_MODULE_NAME = CustomTestRunner.__module__

    def test_make_runner_with_default(self, capsys):
        config = Configuration("")
        runner = RunnerPlugin().make_runner(config)
        assert config.runner == configuration.DEFAULT_RUNNER_CLASS_NAME
        assert isinstance(runner, DefaultRunnerClass)

    def test_make_runner_with_normal_runner_class(self):
        config = Configuration(["--runner=behave.runner:Runner"])
        runner = RunnerPlugin().make_runner(config)
        assert isinstance(runner, DefaultRunnerClass)

    def test_make_runner_with_own_runner_class(self):
        config = Configuration(["--runner=%s:CustomTestRunner" % self.THIS_MODULE_NAME])
        runner = RunnerPlugin().make_runner(config)
        assert isinstance(runner, CustomTestRunner)

    def test_make_runner_with_registered_runner_class(self):
        config = Configuration(["--runner=%s:RegisteredTestRunner" % self.THIS_MODULE_NAME])
        runner = RunnerPlugin().make_runner(config)
        assert isinstance(runner, RegisteredTestRunner)
        assert isinstance(runner, ITestRunner)
        assert issubclass(RegisteredTestRunner, ITestRunner)

    def test_make_runner_with_runner_alias(self):
        config = Configuration(["--runner=custom"])
        config.runner_aliases["custom"] = "%s:CustomTestRunner" % self.THIS_MODULE_NAME
        runner = RunnerPlugin().make_runner(config)
        assert isinstance(runner, CustomTestRunner)

    def test_make_runner_with_runner_alias_from_configfile(self, tmp_path):
        config_file = tmp_path/"behave.ini"
        config_file.write_text(u"""
[behave.runners]
custom = {this_module}:CustomTestRunner
""".format(this_module=self.THIS_MODULE_NAME))

        with use_directory(tmp_path):
            config = Configuration(["--runner=custom"])
            runner = RunnerPlugin().make_runner(config)
            assert isinstance(runner, CustomTestRunner)

    def test_make_runner_fails_with_unknown_module(self, capsys):
        with pytest.raises(ModuleNotFoundError) as exc_info:
            config = Configuration(["--runner=unknown_module:Runner"])
            runner = RunnerPlugin().make_runner(config)
        captured = capsys.readouterr()

        expected = "unknown_module"
        assert exc_info.type is ModuleNotFoundError
        assert exc_info.match(expected)

        # -- OOPS: No output
        print("CAPTURED-OUTPUT: %s;" % captured.out)
        print("CAPTURED-ERROR:  %s;" % captured.err)
        # if six.PY2:
        #     assert "No module named unknown_module" in captured.err
        # else:
        #     assert "No module named 'unknown_module'" in captured.out

    def test_make_runner_fails_with_unknown_class(self, capsys):
        with pytest.raises(ClassNotFoundError) as exc_info:
            config = Configuration(["--runner=behave.runner:UnknownRunner"])
            RunnerPlugin().make_runner(config)

        captured = capsys.readouterr()
        assert "FAILED to load runner.class" in captured.out
        assert "behave.runner:UnknownRunner (ClassNotFoundError)" in captured.out

        expected = "behave.runner:UnknownRunner"
        assert exc_info.type is ClassNotFoundError
        assert exc_info.match(expected)

    def test_make_runner_fails_if_runner_class_is_not_a_class(self):
        with pytest.raises(InvalidClassError) as exc_info:
            config = Configuration(["--runner=%s:INVALID_TEST_RUNNER_CLASS0" % self.THIS_MODULE_NAME])
            RunnerPlugin().make_runner(config)

        expected = "%s:INVALID_TEST_RUNNER_CLASS0: not a class" % self.THIS_MODULE_NAME
        assert exc_info.type is InvalidClassError
        assert exc_info.match(expected)

    def test_make_runner_fails_if_runner_class_is_not_subclass_of_runner_interface(self):
        with pytest.raises(InvalidClassError) as exc_info:
            config = Configuration(["--runner=%s:InvalidTestRunnerNotSubclass" % self.THIS_MODULE_NAME])
            RunnerPlugin().make_runner(config)

        expected = "%s:InvalidTestRunnerNotSubclass: not subclass-of behave.api.runner.ITestRunner" % self.THIS_MODULE_NAME
        assert exc_info.type is InvalidClassError
        assert exc_info.match(expected)

    def test_make_runner_fails_if_runner_class_has_no_ctor(self):
        with pytest.raises(TypeError) as exc_info:
            config = Configuration(["--runner=%s:InvalidTestRunnerWithoutCtor" % self.THIS_MODULE_NAME])
            RunnerPlugin().make_runner(config)

        expected = "Can't instantiate abstract class InvalidTestRunnerWithoutCtor with abstract method(s)? __init__"
        assert exc_info.type is TypeError
        assert exc_info.match(expected)


    def test_make_runner_fails_if_runner_class_has_no_run_method(self):
        with pytest.raises(TypeError) as exc_info:
            config = Configuration(["--runner=%s:InvalidTestRunnerWithoutRun" % self.THIS_MODULE_NAME])
            RunnerPlugin().make_runner(config)

        expected = "Can't instantiate abstract class InvalidTestRunnerWithoutRun with abstract method(s)? run"
        assert exc_info.type is TypeError
        assert exc_info.match(expected)


