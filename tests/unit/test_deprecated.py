# -*- coding: UTF-8 -*-
"""
Unit test facade to protect pytest runner from 3.5 grammar changes:

* Runs tests related to async-steps.
"""

from __future__ import absolute_import, print_function
from behave.capture import CaptureController
from behave.configuration import Configuration
from behave.python_feature import PythonFeature
from behave.runner import Context, ModelRunner
from behave.tag_matcher import ActiveTagMatcher
from mock import Mock
import pytest


# -----------------------------------------------------------------------------
# TEST SUITE -- PYTHON >= 3.5
# -----------------------------------------------------------------------------
if PythonFeature.has_async_function():
    # -- REQUIRES: async/await syntax and coroutine support (since: Python 3.5).
    from ._test_deprecated_py35 import *  # noqa: F403


# -----------------------------------------------------------------------------
# TEST SUITE -- DEPRECATED THINGS
# -----------------------------------------------------------------------------
class TestActiveTagMatcher(object):
    def test_deprecated_should_exclude_with(self):
        active_tag_matcher = ActiveTagMatcher({})
        expected = r"Use 'should_skip_with_tags\(\)' instead"
        with pytest.warns(DeprecationWarning, match=expected):
            _ = active_tag_matcher.should_exclude_with([])

    def test_deprecated_exclude_reason(self):
        active_tag_matcher = ActiveTagMatcher({})
        expected = "Use 'skip_reason' instead"
        with pytest.warns(DeprecationWarning, match=expected):
            _ = active_tag_matcher.exclude_reason

    def test_deprecated_should_run_with(self):
        active_tag_matcher = ActiveTagMatcher({})
        expected = r"Use 'should_run_with_tags\(\)' instead"
        with pytest.warns(DeprecationWarning, match=expected):
            _ = active_tag_matcher.should_run_with([])


class TestConfiguration(object):

    # -- SINCE: behave v1.2.7
    def test_deprecated_use_stdout_capture__as_getter(self):
        """
        Ensure DEPRECATED warning is shown if "stdout_capture" getter is used.
        """
        expected = "Use 'capture_stdout' instead"
        config = Configuration(load_config=False)
        with pytest.warns(DeprecationWarning, match=expected):
            _ = config.stdout_capture

    def test_deprecated_use_stdout_capture__as_setter(self):
        """
        Ensure DEPRECATED warning is shown if "stdout_capture" setter is used.
        """
        expected = "Use 'capture_stdout = ...' instead"
        config = Configuration(load_config=False)
        with pytest.warns(DeprecationWarning, match=expected):
            config.stdout_capture = True

    def test_deprecated_use_stdout_capture__in_ctor(self):
        """
        Ensure DEPRECATED warning is shown if "stdout_capture" is used in CTOR.
        """
        expected = "Use 'capture_stdout = ...' instead"
        with pytest.warns(DeprecationWarning, match=expected):
            _config = Configuration(stdout_capture=True, load_config=False)

    # -- SINCE: behave v1.2.7
    def test_deprecated_use_stderr_capture__as_getter(self):
        """
        Ensure DEPRECATED warning is shown if "stderr_capture" getter is used.
        """
        expected = "Use 'capture_stderr' instead"
        config = Configuration(load_config=False)
        with pytest.warns(DeprecationWarning, match=expected):
            _ = config.stderr_capture

    def test_deprecated_use_stderr_capture__as_setter(self):
        """
        Ensure DEPRECATED warning is shown if "stderr_capture" getter is used.
        """
        expected = "Use 'capture_stderr = ...' instead"
        config = Configuration(load_config=False)
        with pytest.warns(DeprecationWarning, match=expected):
            config.stderr_capture = True

    def test_deprecated_use_stderr_capture__in_ctor(self):
        """
        Ensure DEPRECATED warning is shown if "stderr_capture" is used in CTOR.
        """
        expected = "Use 'capture_stderr = ...' instead"
        with pytest.warns(DeprecationWarning, match=expected):
            _config = Configuration(stderr_capture=True, load_config=False)

    # -- SINCE: behave v1.2.7
    def test_deprecated_use_log_capture__as_getter(self):
        """
        Ensure DEPRECATED warning is shown if "log_capture" getter is used.
        """
        expected = "Use 'capture_log' instead"
        config = Configuration(load_config=False)
        with pytest.warns(DeprecationWarning, match=expected):
            _ = config.log_capture

    def test_deprecated_use_log_capture__as_setter(self):
        """
        Ensure DEPRECATED warning is shown if "log_capture" getter is used.
        """
        expected = "Use 'capture_log = ...' instead"
        config = Configuration(load_config=False)
        with pytest.warns(DeprecationWarning, match=expected):
            config.log_capture = True

    def test_deprecated_use_log_capture__in_ctor(self):
        """
        Ensure DEPRECATED warning is shown if "log_capture" is used in CTOR.
        """
        expected = "Use 'capture_log = ...' instead"
        with pytest.warns(DeprecationWarning, match=expected):
            _config = Configuration(log_capture=True, load_config=False)


class TestCaptureController(object):
    SETUP_CAPTURE_EXPECTED = "setup_capture: Avoid to use 'context' parameter"
    @staticmethod
    def make_context(config):
        runner = Mock(config=config)
        context = Context(runner)
        return context

    # -- SINCE: behave v1.2.7
    def test_deprecated_setup_capture__with_context_param(self):
        config = Configuration(capture=True, load_config=False)
        capture_controller = CaptureController(config)
        context = self.make_context(config)

        # -- USED AS POSITIONAL PARAMETER:
        expected = self.SETUP_CAPTURE_EXPECTED
        with pytest.warns(DeprecationWarning, match=expected):
            capture_controller.setup_capture(context)

    # -- SINCE: behave v1.2.7
    def test_deprecated_setup_capture__with_named_context_param(self):
        config = Configuration(capture=True, load_config=False)
        capture_controller = CaptureController(config)
        context = self.make_context(config)

        # -- USED AS NAMED-PARAMETER:
        expected = self.SETUP_CAPTURE_EXPECTED
        with pytest.warns(DeprecationWarning, match=expected):
            capture_controller.setup_capture(context=context)

    # -- SINCE: behave v1.2.7
    def test_deprecated_use_stdout_capture__as_getter(self):
        """
        Ensure DEPRECATED warning is shown if "stderr_capture" getter is used.
        """
        config = Configuration(load_config=False)
        capture_controller = CaptureController(config)

        expected = "Use 'capture_stdout' instead"
        with pytest.warns(DeprecationWarning, match=expected):
            _ = capture_controller.stdout_capture

    def test_deprecated_use_stdout_capture__as_setter(self):
        """
        Ensure DEPRECATED warning is shown if "stderr_capture" getter is used.
        """
        config = Configuration(load_config=False)
        capture_controller = CaptureController(config)

        expected = "Use 'capture_stdout = ...' instead"
        with pytest.warns(DeprecationWarning, match=expected):
            capture_controller.stdout_capture = "__OOPS__"

    def test_deprecated_use_stderr_capture__as_getter(self):
        """
        Ensure DEPRECATED warning is shown if "stderr_capture" getter is used.
        """
        config = Configuration(load_config=False)
        capture_controller = CaptureController(config)

        expected = "Use 'capture_stderr' instead"
        with pytest.warns(DeprecationWarning, match=expected):
            _ = capture_controller.stderr_capture

    def test_deprecated_use_stderr_capture__as_setter(self):
        """
        Ensure DEPRECATED warning is shown if "stderr_capture" getter is used.
        """
        config = Configuration(load_config=False)
        capture_controller = CaptureController(config)

        expected = "Use 'capture_stderr = ...' instead"
        with pytest.warns(DeprecationWarning, match=expected):
            capture_controller.stderr_capture = "__OOPS__"

    def test_deprecated_use_log_capture__as_getter(self):
        """
        Ensure DEPRECATED warning is shown if "log_capture" getter is used.
        """
        config = Configuration(load_config=False)
        capture_controller = CaptureController(config)

        expected = "Use 'capture_log' instead"
        with pytest.warns(DeprecationWarning, match=expected):
            _ = capture_controller.log_capture

    def test_deprecated_use_log_capture__as_setter(self):
        """
        Ensure DEPRECATED warning is shown if "log_capture" getter is used.
        """
        config = Configuration(load_config=False)
        capture_controller = CaptureController(config)

        expected = "Use 'capture_log = ...' instead"
        with pytest.warns(DeprecationWarning, match=expected):
            capture_controller.log_capture = True


class TestFormatterModule(object):
    def test_deprecated_on_impoort(self):
        expected = "Use 'behave.formatter._registry' instead."
        with pytest.warns(DeprecationWarning, match=expected):
            import behave.formatter.formatters  # noqa: F401


class TestModellRunner(object):
    HOOK_NAMES = [
        "before_all", "after_all",
        "before_feature", "after_feature",
        "before_rule", "after_rule",
        "before_scenario", "after_scenario",
        "before_step", "after_step",
        "before_tag", "after_tag",
    ]
    @staticmethod
    def make_hooks(hook_name):
        def any_hook_func(ctx, *args):
            print("ANY_HOOK: {}".format(args))

        hooks = { hook_name: any_hook_func }
        return hooks

    @classmethod
    def make_runner(cls, hook_name):
        config = Configuration(load_config=False)
        runner = ModelRunner(config)
        runner.hooks = cls.make_hooks(hook_name)
        context = Context(runner)
        runner.context = context
        return runner

    @staticmethod
    def make_hook_args_for(hook_name):
        statement = Mock()
        args = (statement,)
        if "all" in hook_name:
            args = ()
        return args

    # -- SINCE: behave v1.2.7
    @pytest.mark.parametrize("hook_name", HOOK_NAMES)
    def test_deprecated_run_hook__with_context_param(self, hook_name):
        runner = self.make_runner(hook_name)
        context = runner.context
        assert hook_name in runner.hooks, "REQUIRES: Hook exists"

        expected = r"Avoid 'context' in run_hook\(hook_name, context, ...\)"
        with pytest.warns(DeprecationWarning, match=expected):
            args = self.make_hook_args_for(hook_name)
            runner.run_hook(hook_name, context, *args)

    # -- SINCE: behave v1.2.7
    @pytest.mark.parametrize("hook_name", HOOK_NAMES)
    def test_run_hook__without_context_param(self, hook_name):
        # -- BETTER USE: runner.run_hook(hook_name, *args)
        # ENSURE THAT: No DeprecationWarning exists
        runner = self.make_runner(hook_name)
        assert hook_name in runner.hooks, "REQUIRES: Hook exists"
        args = self.make_hook_args_for(hook_name)
        runner.run_hook(hook_name, *args)
