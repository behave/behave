"""
Unit tests for :class:`behave.runner.Context`.
"""

from __future__ import absolute_import, print_function
import unittest
import warnings
from platform import python_implementation

from mock import Mock, patch
import pytest
import six

from behave.configuration import Configuration
from behave.model import Table
from behave.parser import Parser as GherkinParser
from behave.runner import (
    Context, ContextMode, ContextMaskWarning,
    ModelRunner, scoped_context_layer
)
from behave.step_registry import StepRegistry


# -- CONVENIENCE-ALIAS:
_text = six.text_type


class TestContext(object):
    @staticmethod
    def make_runner(config=None):
        if config is None:
            config = Configuration(load_config=False)
        # MAYBE: the_runner = Runner(config)
        the_runner = Mock()
        the_runner.config = config
        return the_runner

    @classmethod
    def make_context(cls, runner=None, **runner_kwargs):
        the_runner = runner
        if the_runner is None:
            the_runner = cls.make_runner(**runner_kwargs)
        context = Context(the_runner)
        return context

    # -- TESTSUITE FOR: behave.runner.Context (PART 1)
    def test_use_or_assign_param__with_existing_param_uses_param(self):
        param_name = "some_param"
        context = self.make_context()
        with context.use_with_user_mode():
            context.some_param = 12
            with scoped_context_layer(context, "scenario"):
                assert param_name in context
                param = context.use_or_assign_param(param_name, 123)
                assert param_name in context
                assert param == 12

    def test_use_or_assign_param__with_nonexisting_param_assigns_param(self):
        param_name = "other_param"
        context = self.make_context()
        with context.use_with_user_mode():
            with scoped_context_layer(context, "scenario"):
                assert param_name not in context
                param = context.use_or_assign_param(param_name, 123)
                assert param_name in context
                assert param == 123

    def test_use_or_create_param__with_existing_param_uses_param(self):
        param_name = "some_param"
        context = self.make_context()
        with context.use_with_user_mode():
            context.some_param = 12
            with scoped_context_layer(context, "scenario"):
                assert param_name in context
                param = context.use_or_create_param(param_name, int, 123)
                assert param_name in context
                assert param == 12

    def test_use_or_create_param__with_nonexisting_param_creates_param(self):
        param_name = "other_param"
        context = self.make_context()
        with context.use_with_user_mode():
            with scoped_context_layer(context, "scenario"):
                assert param_name not in context
                param = context.use_or_create_param(param_name, int, 123)
                assert param_name in context
                assert param == 123

    def test_context_contains(self):
        context = self.make_context()
        assert "thing" not in context
        context.thing = "stuff"
        assert "thing" in context
        context._push()
        assert "thing" in context


class TestContext2(unittest.TestCase):
    # pylint: disable=invalid-name, protected-access, no-self-use

    def setUp(self):
        config = Configuration(load_config=False, verbose=False)
        runner = Mock()
        runner.config = config
        self.config = config
        self.context = Context(runner)

    # -- TESTSUITE FOR: behave.runner.Context (PART 2)
    def test_user_mode_shall_restore_behave_mode(self):
        # -- CASE: No exception is raised.
        initial_mode = ContextMode.BEHAVE
        assert self.context._mode == initial_mode
        with self.context.use_with_user_mode():
            assert self.context._mode == ContextMode.USER
            self.context.thing = "stuff"
        assert self.context._mode == initial_mode

    def test_user_mode_shall_restore_behave_mode_if_assert_fails(self):
        initial_mode = ContextMode.BEHAVE
        assert self.context._mode == initial_mode
        try:
            with self.context.use_with_user_mode():
                assert self.context._mode == ContextMode.USER
                assert False, "XFAIL"
        except AssertionError:
            assert self.context._mode == initial_mode

    def test_user_mode_shall_restore_behave_mode_if_exception_is_raised(self):
        initial_mode = ContextMode.BEHAVE
        assert self.context._mode == initial_mode
        try:
            with self.context.use_with_user_mode():
                assert self.context._mode == ContextMode.USER
                raise RuntimeError("XFAIL")
        except RuntimeError:
            assert self.context._mode == initial_mode

    def test_use_with_user_mode__shall_restore_initial_mode(self):
        # -- CASE: No exception is raised.
        # pylint: disable=protected-access
        initial_mode = ContextMode.BEHAVE
        self.context._mode = initial_mode
        with self.context.use_with_user_mode():
            assert self.context._mode == ContextMode.USER
            self.context.thing = "stuff"
        assert self.context._mode == initial_mode

    def test_use_with_user_mode__shall_restore_initial_mode_with_error(self):
        # -- CASE: Exception is raised.
        # pylint: disable=protected-access
        initial_mode = ContextMode.BEHAVE
        self.context._mode = initial_mode
        try:
            with self.context.use_with_user_mode():
                assert self.context._mode == ContextMode.USER
                raise RuntimeError("XFAIL")
        except RuntimeError:
            assert self.context._mode == initial_mode

    def test_use_with_behave_mode__shall_restore_initial_mode(self):
        # -- CASE: No exception is raised.
        # pylint: disable=protected-access
        initial_mode = ContextMode.USER
        self.context._mode = initial_mode
        with self.context._use_with_behave_mode():
            assert self.context._mode == ContextMode.BEHAVE
            self.context.thing = "stuff"
        assert self.context._mode == initial_mode

    def test_use_with_behave_mode__shall_restore_initial_mode_with_error(self):
        # -- CASE: Exception is raised.
        # pylint: disable=protected-access
        initial_mode = ContextMode.USER
        self.context._mode = initial_mode
        try:
            with self.context._use_with_behave_mode():
                assert self.context._mode == ContextMode.BEHAVE
                raise RuntimeError("XFAIL")
        except RuntimeError:
            assert self.context._mode == initial_mode

    def test_attribute_set_at_upper_level_visible_at_lower_level(self):
        self.context.thing = "stuff"
        self.context._push()
        assert self.context.thing == "stuff"

    def test_attribute_set_at_lower_level_not_visible_at_upper_level(self):
        self.context._push()
        self.context.thing = "stuff"
        self.context._pop()
        assert getattr(self.context, "thing", None) is None

    def test_attributes_set_at_upper_level_visible_at_lower_level(self):
        self.context.thing = "stuff"
        self.context._push()
        assert self.context.thing == "stuff"
        self.context.other_thing = "more stuff"
        self.context._push()
        assert self.context.thing == "stuff"
        assert self.context.other_thing == "more stuff"
        self.context.third_thing = "wombats"
        self.context._push()
        assert self.context.thing == "stuff"
        assert self.context.other_thing == "more stuff"
        assert self.context.third_thing == "wombats"

    def test_attributes_set_at_lower_level_not_visible_at_upper_level(self):
        self.context.thing = "stuff"

        self.context._push()
        self.context.other_thing = "more stuff"

        self.context._push()
        self.context.third_thing = "wombats"
        assert self.context.thing == "stuff"
        assert self.context.other_thing == "more stuff"
        assert self.context.third_thing == "wombats"

        self.context._pop()
        assert self.context.thing == "stuff"
        assert self.context.other_thing == "more stuff"
        assert getattr(self.context, "third_thing", None) is None, \
               "%s is not None" % self.context.third_thing

        self.context._pop()
        assert self.context.thing == "stuff"
        assert getattr(self.context, "other_thing", None) is None, \
               "%s is not None" % self.context.other_thing
        assert getattr(self.context, "third_thing", None) is None, \
               "%s is not None" % self.context.third_thing

    def test_masking_existing_user_attribute_when_verbose_causes_warning(self):
        warns = []

        def catch_warning(*args, **kwargs):
            warns.append(args[0])

        old_showwarning = warnings.showwarning
        warnings.showwarning = catch_warning

        # pylint: disable=protected-access
        self.config.verbose = True
        with self.context.use_with_user_mode():
            self.context.thing = "stuff"
            self.context._push()
            self.context.thing = "other stuff"

        warnings.showwarning = old_showwarning

        print(repr(warns))
        assert warns, "warns is empty!"
        warning = warns[0]
        assert isinstance(warning, ContextMaskWarning), "warning is not a ContextMaskWarning"
        info = warning.args[0]
        assert info.startswith("user code"), "%r doesn't start with 'user code'" % info
        assert "'thing'" in info, "%r not in %r" % ("'thing'", info)
        assert "tutorial" in info, '"tutorial" not in %r' % (info, )

    def test_masking_existing_user_attribute_when_not_verbose_causes_no_warning(self):
        warns = []

        def catch_warning(*args, **kwargs):
            warns.append(args[0])

        old_showwarning = warnings.showwarning
        warnings.showwarning = catch_warning

        # explicit
        # pylint: disable=protected-access
        self.config.verbose = False
        with self.context.use_with_user_mode():
            self.context.thing = "stuff"
            self.context._push()
            self.context.thing = "other stuff"

        warnings.showwarning = old_showwarning

        assert not warns

    def test_behave_masking_user_attribute_causes_warning(self):
        warns = []

        def catch_warning(*args, **kwargs):
            warns.append(args[0])

        old_showwarning = warnings.showwarning
        warnings.showwarning = catch_warning

        with self.context.use_with_user_mode():
            self.context.thing = "stuff"
        # pylint: disable=protected-access
        self.context._push()
        self.context.thing = "other stuff"

        warnings.showwarning = old_showwarning

        print(repr(warns))
        assert warns, "OOPS: warns is empty, but expected non-empty"
        warning = warns[0]
        assert isinstance(warning, ContextMaskWarning), "warning is not a ContextMaskWarning"
        info = warning.args[0]
        assert info.startswith("behave runner"), "%r doesn't start with 'behave runner'" % info
        assert "'thing'" in info, "%r not in %r" % ("'thing'", info)
        filename = __file__.rsplit(".", 1)[0]
        if python_implementation() == "Jython":
            filename = filename.replace("$py", ".py")
        assert filename in info, "%r not in %r" % (filename, info)

    def test_setting_root_attribute_that_masks_existing_causes_warning(self):
        # pylint: disable=protected-access
        warns = []

        def catch_warning(*args, **kwargs):
            warns.append(args[0])

        old_showwarning = warnings.showwarning
        warnings.showwarning = catch_warning

        with self.context.use_with_user_mode():
            self.context._push()
            self.context.thing = "teak"
        self.context._set_root_attribute("thing", "oak")

        warnings.showwarning = old_showwarning

        print(repr(warns))
        assert warns
        warning = warns[0]
        assert isinstance(warning, ContextMaskWarning)
        info = warning.args[0]
        assert info.startswith("behave runner"), "%r doesn't start with 'behave runner'" % info
        assert "'thing'" in info, "%r not in %r" % ("'thing'", info)
        filename = __file__.rsplit(".", 1)[0]
        if python_implementation() == "Jython":
            filename = filename.replace("$py", ".py")
        assert filename in info, "%r not in %r" % (filename, info)

    def test_context_deletable(self):
        assert "thing" not in self.context
        self.context.thing = "stuff"
        assert "thing" in self.context
        del self.context.thing
        assert "thing" not in self.context

    # OLD: @raises(AttributeError)
    def test_context_deletable_raises(self):
        # pylint: disable=protected-access
        assert "thing" not in self.context
        self.context.thing = "stuff"
        assert "thing" in self.context
        self.context._push()
        assert "thing" in self.context
        with pytest.raises(AttributeError):
            del self.context.thing


class ExampleSteps(object):
    text = None
    table = None

    @staticmethod
    def step_passes(context):   # pylint: disable=unused-argument
        pass

    @staticmethod
    def step_fails(context):    # pylint: disable=unused-argument
        assert False, "XFAIL"

    @classmethod
    def step_with_text(cls, context):
        assert context.text is not None, "REQUIRE: multi-line text"
        cls.text = context.text

    @classmethod
    def step_with_table(cls, context):
        assert context.table, "REQUIRE: table"
        cls.table = context.table

    @classmethod
    def register_steps_with(cls, step_registry):
        # pylint: disable=bad-whitespace
        step_definitions = [
            ("step", "a step passes", cls.step_passes),
            ("step", "a step fails",  cls.step_fails),
            ("step", "a step with text:",     cls.step_with_text),
            ("step", "a step with a table:",  cls.step_with_table),
        ]
        for keyword, pattern, func in step_definitions:
            step_registry.add_step_definition(keyword, pattern, func)


class TestContext_ExecuteSteps(unittest.TestCase):
    """
    Test the behave.runner.Context.execute_steps() functionality.
    """
    # pylint: disable=invalid-name, no-self-use
    step_registry = None

    def setUp(self):
        if not self.step_registry:
            # -- SETUP ONCE:
            self.step_registry = StepRegistry()
            ExampleSteps.register_steps_with(self.step_registry)
        ExampleSteps.text = None
        ExampleSteps.table = None
        config = Configuration(load_config=False,
                               verbose=False,
                               dry_run=False,
                               capture_output=False,
                               capture_errors=False,
                               capture_log=False,
                               logging_format=None,
                               logging_datefmt=None,
        )
        # -- SAME AS:
        # config.verbose = False
        # config.dry_run = False
        # config.capture_stdout = False
        # config.capture_stderr = False
        # config.capture_log = False
        # config.logging_format = None
        # config.logging_datefmt = None
        runner = ModelRunner(config)
        runner.step_registry = self.step_registry

        context = Context(runner)
        context.feature = Mock()
        context.feature.parser = GherkinParser()
        runner.context = context
        self.config = config
        self.context = context
        self.context.runner = runner

    def test_execute_steps_with_simple_steps(self):
        doc = u"""
Given a step passes
Then a step passes
""".lstrip()
        with patch("behave.step_registry.registry", self.step_registry):
            result = self.context.execute_steps(doc)
            assert result is True

    def test_execute_steps_with_failing_step(self):
        doc = u"""
Given a step passes
When a step fails
Then a step passes
""".lstrip()
        with patch("behave.step_registry.registry", self.step_registry):
            try:
                _result = self.context.execute_steps(doc)
            except AssertionError as e:
                assert "FAILED SUB-STEP: When a step fails" in _text(e)

    def test_execute_steps_with_undefined_step(self):
        doc = u"""
Given a step passes
When a step is undefined
Then a step passes
""".lstrip()
        with patch("behave.step_registry.registry", self.step_registry):
            try:
                _result = self.context.execute_steps(doc)
            except AssertionError as e:
                assert "UNDEFINED SUB-STEP: When a step is undefined" in _text(e)

    def test_execute_steps_with_text(self):
        doc = u'''
Given a step passes
When a step with text:
    """
    Lorem ipsum
    Ipsum lorem
    """
Then a step passes
'''.lstrip()
        with patch("behave.step_registry.registry", self.step_registry):
            result = self.context.execute_steps(doc)
            expected_text = "Lorem ipsum\nIpsum lorem"
            assert result is True
            assert expected_text == ExampleSteps.text

    def test_execute_steps_with_table(self):
        doc = u"""
Given a step with a table:
    | Name  | Age |
    | Alice |  12 |
    | Bob   |  23 |
Then a step passes
""".lstrip()
        with patch("behave.step_registry.registry", self.step_registry):
            # pylint: disable=bad-whitespace, bad-continuation
            result = self.context.execute_steps(doc)
            expected_table = Table([u"Name", u"Age"], rows=[
                    [u"Alice", u"12"],
                    [u"Bob",   u"23"],
                ], line=0
            )
            assert result is True
            assert expected_table == ExampleSteps.table

    def test_context_table_is_restored_after_execute_steps_without_table(self):
        doc = u"""
Given a step passes
Then a step passes
""".lstrip()
        with patch("behave.step_registry.registry", self.step_registry):
            original_table = "<ORIGINAL_TABLE>"
            self.context.table = original_table
            self.context.execute_steps(doc)
            assert self.context.table == original_table

    def test_context_table_is_restored_after_execute_steps_with_table(self):
        doc = u"""
Given a step with a table:
    | Name  | Age |
    | Alice |  12 |
    | Bob   |  23 |
Then a step passes
""".lstrip()
        with patch("behave.step_registry.registry", self.step_registry):
            original_table = "<ORIGINAL_TABLE>"
            self.context.table = original_table
            self.context.execute_steps(doc)
            assert self.context.table == original_table

    def test_context_text_is_restored_after_execute_steps_without_text(self):
        doc = u"""
Given a step passes
Then a step passes
""".lstrip()
        with patch("behave.step_registry.registry", self.step_registry):
            original_text = "<ORIGINAL_TEXT>"
            self.context.text = original_text
            self.context.execute_steps(doc)
            assert self.context.text == original_text

    def test_context_text_is_restored_after_execute_steps_with_text(self):
        doc = u'''
Given a step passes
When a step with text:
    """
    Lorem ipsum
    Ipsum lorem
    """
'''.lstrip()
        with patch("behave.step_registry.registry", self.step_registry):
            original_text = "<ORIGINAL_TEXT>"
            self.context.text = original_text
            self.context.execute_steps(doc)
            assert self.context.text == original_text


    # OLD: @raises(ValueError)
    def test_execute_steps_should_fail_when_called_without_feature(self):
        doc = u"""
Given a passes
Then a step passes
""".lstrip()
        with patch("behave.step_registry.registry", self.step_registry):
            self.context.feature = None
            with pytest.raises(ValueError):
                self.context.execute_steps(doc)
