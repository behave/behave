"""
Tests for :mod:`behave.runner` related to hook processing.
"""

from __future__ import absolute_import, print_function
from mock import Mock
from behave.capture import CaptureSinkAsCollector
from behave.configuration import Configuration
from behave.runner import Context, ModelRunner

import pytest


todo = pytest.mark.todo()
not_implemented = pytest.mark.not_implemented()


# -----------------------------------------------------------------------------
# TEST SUPPORT
# -----------------------------------------------------------------------------
class SomeError(RuntimeError):
    pass

# -- HOOKS
def good_hook(ctx, *args, **kwargs):
    print("CALLED: good_hook")


def good_hook_show_any(ctx, *args, **kwargs):
    print("CALLED: good_hook_show_any")
good_hook_show_any.show_capture_on_success = True


def bad_hook_assert(ctx, *args, **kwargs):
    print("CALLED: bad_hook_assert")
    assert False, "OOPS: bad_hook_assert"


def bad_hook_error(ctx, *args, **kwargs):
    print("CALLED: bad_hook_error")
    raise SomeError("OOPS: bad_hook_error")

# -- HOOK FUNCTIONS WITH TAG:
def good_tag_hook(ctx, tag):
    print("CALLED: good_tag_hook -- tag={}".format(tag))

def bad_tag_hook_error(ctx, tag):
    print("CALLED: bad_tag_hook_error -- tag={}".format(tag))
    raise SomeError("OOPS: bad_tag_hook_error")

def select_hook_func_by_tag(tag):
    hook_func = good_tag_hook
    if tag.startswith("bad_"):
        hook_func = bad_tag_hook_error
    return hook_func

def any_tag_hook(ctx, tag):
    hook_func = select_hook_func_by_tag(tag)
    hook_func(ctx, tag)


# -----------------------------------------------------------------------------
# TEST SUITE
# -----------------------------------------------------------------------------
class TestRunHooks(object):

    @staticmethod
    def make_runner(**config_data):
        config = Configuration(load_config=False, **config_data)
        runner = ModelRunner(config)
        runner.context = Context(runner)
        return runner

    @classmethod
    def make_runner_with_hook(cls, hook_name, hook_func, **config_data):
        runner = cls.make_runner(**config_data)
        runner.hooks[hook_name] = hook_func
        return runner

    def test_should_run_hook__true_if_hook_exists(self):
        hook_name = "some_hook"
        hook_func = good_hook
        runner = self.make_runner_with_hook(hook_name, hook_func)

        result = runner.should_run_hook(hook_name)
        assert result is True
        assert hook_name in runner.hooks

    def test_should_run_hook__false_if_hook_not_exists(self):
        missing_hook_name = "missing_hook"
        runner = self.make_runner()

        result = runner.should_run_hook(missing_hook_name)
        assert result is False
        assert missing_hook_name not in runner.hooks

    def test_should_capture_hook__true_if_capture_enabled_and_hook_exists(self):
        hook_name = "some_hook"
        hook_func = good_hook
        runner = self.make_runner_with_hook(hook_name, hook_func,
                                            capture=True,
                                            capture_hooks=True)
        # -- PRECONDITIONS:
        assert hook_name in runner.hooks
        assert runner.config.capture_hooks is True
        assert runner.config.should_capture_hooks() is True

        result = runner.should_capture_hook(hook_name)
        assert result is True

    def test_should_capture_hook__false_if_hook_not_exists(self):
        missing_hook_name = "missing_hook"
        runner = self.make_runner(capture=True, capture_hooks=True)
        # -- PRECONDITIONS:
        assert missing_hook_name not in runner.hooks
        assert runner.config.should_capture_hooks() is True

        result = runner.should_capture_hook(missing_hook_name)
        assert result is False

    def test_should_capture_hook__false_on_capture_hooks_disabled(self):
        hook_name = "some_hook"
        hook_func = good_hook
        runner = self.make_runner_with_hook(hook_name, hook_func,
                                            capture=True,
                                            capture_hooks=False)
        # -- PRECONDITIONS:
        assert hook_name in runner.hooks
        assert runner.config.should_capture() is True
        assert runner.config.should_capture_hooks() is False

        result = runner.should_capture_hook(hook_name)
        assert result is False

    def test_should_capture_hook__false_on_capture_disabled(self):
        hook_name = "some_hook"
        hook_func = good_hook
        runner = self.make_runner_with_hook(hook_name, hook_func,
                                            capture=False,
                                            capture_hooks=True)

        # -- PRECONDITIONS:
        assert hook_name in runner.hooks
        assert runner.config.capture_hooks is True
        assert runner.config.should_capture() is False
        assert runner.config.should_capture_hooks() is False

        result = runner.should_capture_hook(hook_name)
        assert result is False

    # -- FUNCTION: run_hook_with_capture()
    def test_run_hook_with_capture__good_case(self):
        hook_name = "before_scenario"
        hook_func = good_hook_show_any
        runner = self.make_runner_with_hook(hook_name, hook_func)
        assert hook_name in runner.hooks
        assert runner.config.should_capture_hooks() is True

        # CaptureSinkAsCollector.STORE_ON_SUCCESS = True
        # capture_sink = CaptureSinkAsCollector()
        statement = Mock()
        args = (statement,)
        capture_sink = CaptureSinkAsCollector(store_on_success=True)
        result = runner.run_hook_with_capture(hook_name, *args,
                                              capture_sink=capture_sink)
        output = capture_sink.make_output()
        assert result is True  # -- HOOK_PASSED
        assert "CALLED: good_hook_show_any" in output
        # print("\nCOLLECTED_CAPTURED_OUTPUT:\n{output}".format(output=output))

    def test_run_hook_with_capture__bad_case_if_hook_assert_fails(self):
        hook_name = "before_scenario"
        hook_func = bad_hook_assert
        runner = self.make_runner_with_hook(hook_name, hook_func)
        assert hook_name in runner.hooks
        assert runner.config.should_capture_hooks() is True

        statement = Mock()
        statement.error_message = u""
        args = (statement,)

        capture_sink = CaptureSinkAsCollector()
        result = runner.run_hook_with_capture(hook_name, *args,
                                              capture_sink=capture_sink)
        output = capture_sink.make_output()
        expected = "HOOK-ERROR in before_scenario: AssertionError: OOPS: bad_hook_assert"
        assert result is False  # -- HOOK_FAILED
        assert "CALLED: bad_hook_assert" in output
        assert expected in output
        # print("\nCOLLECTED_CAPTURED_OUTPUT:\n{output}".format(output=output))

    def test_run_hook_with_capture__bad_case_if_hook_raises_error(self):
        hook_name = "before_step"
        hook_func = bad_hook_error
        runner = self.make_runner_with_hook(hook_name, hook_func)
        assert hook_name in runner.hooks
        assert runner.config.should_capture_hooks() is True

        statement = Mock()
        statement.error_message = u""
        args = (statement,)

        capture_sink = CaptureSinkAsCollector()
        result = runner.run_hook_with_capture(hook_name, *args,
                                              capture_sink=capture_sink)
        output = capture_sink.make_output()
        expected = "HOOK-ERROR in before_step: SomeError: OOPS: bad_hook_error"
        assert result is False  # -- HOOK_FAILED
        assert "CALLED: bad_hook_error" in output
        assert expected in output

    def test_run_hook_with_capture__no_output_if_capture_hooks_is_disabled(self, capsys):
        hook_name = "good_hook"
        hook_func = good_hook
        runner = self.make_runner_with_hook(hook_name, hook_func,
                                            capture=True,
                                            capture_hooks=False)
        assert runner.config.should_capture_hooks() is False

        statement = Mock()
        statement.error_message = u""
        args = (statement,)
        capture_sink = CaptureSinkAsCollector()
        result = runner.run_hook_with_capture(hook_name, *args,
                                              capture_sink=capture_sink)
        output = capture_sink.make_output()
        assert result is True  # -- HOOK_PASSED
        assert "CALLED: good_hook" not in output
        assert output == ""

        # -- NON-CAPTURED_OUTPUT:
        non_captured_output = capsys.readouterr().out
        print(non_captured_output)
        assert "CALLED: good_hook" in non_captured_output

    def test_run_hook_with_capture__no_output_if_hook_not_exists(self):
        hook_name = "missing_hook"
        runner = self.make_runner(capture=True, capture_hooks=True)
        assert runner.config.should_capture_hooks() is True

        statement = Mock()
        statement.error_message = u""
        args = (statement,)
        capture_sink = CaptureSinkAsCollector()
        result = runner.run_hook_with_capture(hook_name, *args,
                                              capture_sink=capture_sink)
        output = capture_sink.make_output()
        assert result is True  # -- HOOK_PASSED
        assert output == ""

    def test_run_hook_with_capture__good_with_default_capture_sink(self):
        hook_name = "before_xxx"
        hook_func = good_hook_show_any
        runner = self.make_runner_with_hook(hook_name, hook_func)
        assert hook_name in runner.hooks
        assert runner.config.should_capture_hooks() is True

        statement = Mock()
        args = (statement,)
        capture_sink = runner.capture_sink
        capture_sink.store_on_success = True
        result = runner.run_hook_with_capture(hook_name, *args)
        output = capture_sink.make_output()
        assert result is True  # -- HOOK_PASSED
        assert "CALLED: good_hook_show_any" in output

    def test_run_hook_with_capture__bad_with_default_capture_sink(self):
        hook_name = "before_zzz"
        hook_func = bad_hook_error
        runner = self.make_runner_with_hook(hook_name, hook_func)
        assert hook_name in runner.hooks
        assert runner.config.should_capture_hooks() is True

        statement = Mock()
        statement.error_message = u""
        args = (statement,)
        capture_sink = runner.capture_sink
        result = runner.run_hook_with_capture(hook_name, *args)
        output = capture_sink.make_output()
        expected = "HOOK-ERROR in before_zzz: SomeError: OOPS: bad_hook_error"
        assert result is False  # -- HOOK_FAILED
        assert "CALLED: bad_hook_error" in output
        assert expected in output

    # -- FUNCTION: run_hook_tags_with_capture()
    def test_run_hook_tags_with_capture__one_captured_output_section(self):
        hook_name = "before_tag"
        hook_func = any_tag_hook
        runner = self.make_runner_with_hook(hook_name, hook_func)
        assert hook_name in runner.hooks
        assert runner.config.should_capture_hooks() is True

        tags = ["good_alice", "good_bob"]
        capture_sink = CaptureSinkAsCollector(store_on_success=True)
        result = runner.run_hook_tags_with_capture(hook_name, tags,
                                                   capture_sink=capture_sink)
        output = capture_sink.make_report()
        expected = """
----
CAPTURED STDOUT: before_tag
CALLED: good_tag_hook -- tag=good_alice
CALLED: good_tag_hook -- tag=good_bob
----
""".strip()
        # -- INTENTION: One captured-output section for all tags.
        assert expected in output
        assert result is True  # -- HOOK_PASSED

    def test_run_hook_tags_with_capture__continues_after_error(self):
        hook_name = "after_tag"
        hook_func = any_tag_hook
        runner = self.make_runner_with_hook(hook_name, hook_func)
        assert hook_name in runner.hooks
        assert runner.config.should_capture_hooks() is True

        tags = ["good_alice", "bad_bob", "good_charly"]
        capture_sink = CaptureSinkAsCollector()
        result = runner.run_hook_tags_with_capture(hook_name, tags,
                                                   capture_sink=capture_sink)
        output = capture_sink.make_report()
        expected = """
----
CAPTURED STDOUT: after_tag
CALLED: good_tag_hook -- tag=good_alice
CALLED: bad_tag_hook_error -- tag=bad_bob
HOOK-ERROR in after_tag(tag=bad_bob): SomeError: OOPS: bad_tag_hook_error
CALLED: good_tag_hook -- tag=good_charly
""".strip()
        # -- INTENTION: Continues over tags even if error occurs.
        assert expected in output
        assert result is False  # -- SOME HOOK_FAILED
