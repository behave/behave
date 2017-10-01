# -*- coding: UTF-8 -*-
"""
Unit tests for :mod:`behave.fixture` module.
"""

from __future__ import absolute_import, print_function
import sys
import inspect
from behave.fixture import \
    fixture, use_fixture, is_context_manager, InvalidFixtureError, \
    use_fixture_by_tag, use_composite_fixture_with, fixture_call_params
from behave.runner import Context, CleanupError, scoped_context_layer
from behave._types import Unknown
import pytest
from mock import Mock
import six


# -----------------------------------------------------------------------------
# TEST SUPPORT
# -----------------------------------------------------------------------------
def make_runtime_context(runner=None):
    """Build a runtime/runner context for the tests here (partly faked).
    
    :return: Runtime context object (normally used by the runner).
    """
    if runner is None:
        runner = Mock()
        runner.config = Mock()
    return Context(runner)


class BasicFixture(object):
    """Helper class used in behave fixtures (test-support)."""
    def __init__(self, *args, **kwargs):
        setup_called = kwargs.pop("_setup_called", True)
        name = kwargs.get("name", self.__class__.__name__)
        self.name = name
        self.args = args
        self.kwargs = kwargs.copy()
        self.setup_called = setup_called
        self.cleanup_called = False

    def __del__(self):
        if not self.cleanup_called:
            # print("LATE-CLEANUP (in dtor): %s" % self.name)
            self.cleanup()

    @classmethod
    def setup(cls, *args, **kwargs):
        name = kwargs.get("name", cls.__name__)
        print("%s.setup: %s, kwargs=%r" % (cls.__name__, name, kwargs))
        kwargs["_setup_called"] = True
        return cls(*args, **kwargs)

    def cleanup(self):
        self.cleanup_called = True
        print("%s.cleanup: %s" % (self.__class__.__name__, self.name))

    def __str__(self):
        args_text = ", ".join([str(arg) for arg in self.args])
        kwargs_parts = ["%s= %s" % (key, value)
            for key, value in sorted(six.iteritems(self.kwargs))]
        kwargs_text = ", ".join(kwargs_parts)
        return "%s: args=%s; kwargs=%s" % (self.name, args_text, kwargs_text)


class FooFixture(BasicFixture): pass
class BarFixture(BasicFixture): pass

# -- FIXTURE EXCEPTIONS:
class FixtureSetupError(RuntimeError): pass
class FixtureCleanupError(RuntimeError): pass


# -----------------------------------------------------------------------------
# CUSTOM ASSERTIONS:
# -----------------------------------------------------------------------------
def assert_context_setup(context, fixture_name, fixture_class=Unknown):
    """Ensure that fixture object is stored in context."""
    the_fixture = getattr(context, fixture_name, Unknown)
    assert hasattr(context, fixture_name)
    assert the_fixture is not Unknown
    if fixture_class is not Unknown:
        assert isinstance(the_fixture, fixture_class)

def assert_context_cleanup(context, fixture_name):
    """Ensure that fixture object is no longer stored in context."""
    assert not hasattr(context, fixture_name)

def assert_fixture_setup_called(fixture_obj):
    """Ensure that fixture setup was performed."""
    if hasattr(fixture_obj, "setup_called"):
        assert fixture_obj.setup_called

def assert_fixture_cleanup_called(fixture_obj):
    if hasattr(fixture_obj, "cleanup_called"):
        assert fixture_obj.cleanup_called

def assert_fixture_cleanup_not_called(fixture_obj):
    if hasattr(fixture_obj, "cleanup_called"):
        assert not fixture_obj.cleanup_called


# -----------------------------------------------------------------------------
# TEST SUITE:
# -----------------------------------------------------------------------------
class TestFixtureDecorator(object):
    def test_decorator(self):
        @fixture
        def foo(context, *args, **kwargs):
            pass

        assert foo.behave_fixture == True
        assert foo.name is None
        assert foo.pattern is None
        assert callable(foo)

    def test_decorator_call_without_params(self):
        @fixture()
        def bar0(context, *args, **kwargs):
            pass

        assert bar0.behave_fixture == True
        assert bar0.name is None
        assert bar0.pattern is None
        assert callable(bar0)

    def test_decorator_call_with_name(self):
        @fixture(name="fixture.bar2")
        def bar1(context, *args, **kwargs):
            pass

        assert bar1.behave_fixture == True
        assert bar1.name == "fixture.bar2"
        assert bar1.pattern is None
        assert callable(bar1)

    def test_decorated_generator_function_is_callable(self):
        # -- SIMILAR-TO: TestUseFixture.test_with_generator_func()
        @fixture
        def foo(context, *args, **kwargs):
            fixture_object = FooFixture.setup(*args, **kwargs)
            yield fixture_object
            fixture_object.cleanup()

        # -- ENSURE: Decorated fixture function can be called w/ params.
        context = None
        func_it = foo(context, 1, 2, 3, name="foo_1")

        # -- VERIFY: Expectations
        assert is_context_manager(foo)
        assert inspect.isfunction(foo)
        assert inspect.isgenerator(func_it)


    def test_decorated_function_is_callable(self):
        # -- SIMILAR-TO: TestUseFixture.test_with_function()
        @fixture(name="fixture.bar")
        def bar(context, *args, **kwargs):
            fixture_object = BarFixture.setup(*args, **kwargs)
            return fixture_object

        # -- ENSURE: Decorated fixture function can be called w/ params.
        context = None
        the_fixture = bar(context, 3, 2, 1, name="bar_1")

        # -- VERIFY: Expectations
        assert inspect.isfunction(bar)
        assert isinstance(the_fixture, BarFixture)

    def test_decorator_with_non_callable_raises_type_error(self):
        class NotCallable(object): pass

        with pytest.raises(TypeError) as exc_info:
            not_callable = NotCallable()
            bad_fixture = fixture(not_callable)     # DECORATED_BY_HAND

        exception_text = str(exc_info.value)
        assert "Invalid func:" in exception_text
        assert "NotCallable object" in exception_text

class TestUseFixture(object):

    def test_basic_lifecycle(self):
        # -- NOTE: Use explicit checks instead of assert-helper functions.
        @fixture
        def foo(context, checkpoints, *args, **kwargs):
            checkpoints.append("foo.setup")
            yield FooFixture()
            checkpoints.append("foo.cleanup")

        checkpoints = []
        context = make_runtime_context()
        with scoped_context_layer(context):
            the_fixture = use_fixture(foo, context, checkpoints)
            # -- ENSURE: Fixture setup is performed (and as expected)
            assert isinstance(the_fixture, FooFixture)
            assert checkpoints == ["foo.setup"]
            checkpoints.append("scoped-block")

        # -- ENSURE: Fixture cleanup was performed
        assert checkpoints == ["foo.setup", "scoped-block", "foo.cleanup"]

    def test_fixture_with_args(self):
        """Ensures that positional args are passed to fixture function."""
        @fixture
        def foo(context, *args, **kwargs):
            fixture_object = FooFixture.setup(*args, **kwargs)
            context.foo = fixture_object
            yield fixture_object
            fixture_object.cleanup()

        context = make_runtime_context()
        with scoped_context_layer(context):
            the_fixture = use_fixture(foo, context, 1, 2, 3)

        expected_args = (1, 2, 3)
        assert the_fixture.args == expected_args

    def test_fixture_with_kwargs(self):
        """Ensures that keyword args are passed to fixture function."""
        @fixture
        def bar(context, *args, **kwargs):
            fixture_object = BarFixture.setup(*args, **kwargs)
            context.bar = fixture_object
            return fixture_object

        context = make_runtime_context()
        with scoped_context_layer(context):
            the_fixture = use_fixture(bar, context, name="bar", timeout=10)

        expected_kwargs = dict(name="bar", timeout=10)
        assert the_fixture.kwargs == expected_kwargs

    def test_with_generator_function(self):
        @fixture
        def foo(context, checkpoints, *args, **kwargs):
            checkpoints.append("foo.setup")
            fixture_object = FooFixture.setup(*args, **kwargs)
            context.foo = fixture_object
            yield fixture_object
            fixture_object.cleanup()
            checkpoints.append("foo.cleanup.done")

        checkpoints = []
        context = make_runtime_context()
        with scoped_context_layer(context):
            the_fixture = use_fixture(foo, context, checkpoints)
            assert_context_setup(context, "foo", FooFixture)
            assert_fixture_setup_called(the_fixture)
            assert_fixture_cleanup_not_called(the_fixture)
            assert checkpoints == ["foo.setup"]
            print("Do something...")
        assert_context_cleanup(context, "foo")
        assert_fixture_cleanup_called(the_fixture)
        assert checkpoints == ["foo.setup", "foo.cleanup.done"]

    def test_with_function(self):
        @fixture
        def bar(context, checkpoints, *args, **kwargs):
            checkpoints.append("bar.setup")
            fixture_object = BarFixture.setup(*args, **kwargs)
            context.bar = fixture_object
            return fixture_object

        checkpoints = []
        context = make_runtime_context()
        with scoped_context_layer(context):
            the_fixture = use_fixture(bar, context, checkpoints)
            assert_context_setup(context, "bar", BarFixture)
            assert_fixture_setup_called(the_fixture)
            assert_fixture_cleanup_not_called(the_fixture)
            assert checkpoints == ["bar.setup"]
            print("Do something...")
        assert_context_cleanup(context, "foo")
        assert_fixture_cleanup_not_called(the_fixture)
        # -- NOT: Normal functions have no fixture-cleanup part.

    def test_can_use_fixture_two_times(self):
        """Ensures that a fixture can be used multiple times 
        (with different names) within a context layer.
        """
        @fixture
        def foo(context, checkpoints, *args, **kwargs):
            fixture_object = FooFixture.setup(*args, **kwargs)
            setattr(context, fixture_object.name, fixture_object)
            checkpoints.append("foo.setup:%s" % fixture_object.name)
            yield fixture_object
            checkpoints.append("foo.cleanup:%s" % fixture_object.name)
            fixture_object.cleanup()

        checkpoints = []
        context = make_runtime_context()
        with scoped_context_layer(context):
            the_fixture1 = use_fixture(foo, context, checkpoints, name="foo_1")
            the_fixture2 = use_fixture(foo, context, checkpoints, name="foo_2")
            # -- VERIFY: Fixture and context setup was performed.
            assert checkpoints == ["foo.setup:foo_1", "foo.setup:foo_2"]
            assert context.foo_1 is the_fixture1
            assert context.foo_2 is the_fixture2
            assert the_fixture1 is not the_fixture2

            checkpoints.append("scoped-block")

        # -- VERIFY: Fixture and context cleanup is performed.
        assert_context_cleanup(context, "foo_1")
        assert_context_cleanup(context, "foo_2")
        assert checkpoints == ["foo.setup:foo_1",   "foo.setup:foo_2",
                               "scoped-block",
                               "foo.cleanup:foo_2", "foo.cleanup:foo_1"]
        # -- NOTE: Cleanups occur in reverse order.

    def test_invalid_fixture_function(self):
        """Test invalid generator function with more than one yield-statement
        (not a valid fixture/context-manager).
        """
        @fixture
        def invalid_fixture(context, checkpoints, *args, **kwargs):
            checkpoints.append("bad.setup")
            yield FooFixture(*args, **kwargs)
            checkpoints.append("bad.cleanup")
            yield None  # -- SYNDROME HERE: More than one yield-statement

        # -- PERFORM-TEST:
        checkpoints = []
        context = make_runtime_context()
        with pytest.raises(InvalidFixtureError):
            with scoped_context_layer(context):
                the_fixture = use_fixture(invalid_fixture, context, checkpoints)
                assert checkpoints == ["bad.setup"]
                checkpoints.append("scoped-block")

        # -- VERIFY: Ensure normal cleanup-parts were performed.
        assert checkpoints == ["bad.setup", "scoped-block", "bad.cleanup"]

    def test_bad_with_setup_error(self):
        # -- SAD: cleanup_fixture() part is called when setup-error occurs,
        #    but not the cleanup-part of the generator (generator-magic).
        @fixture
        def bad_with_setup_error(context, checkpoints, *args, **kwargs):
            checkpoints.append("bad.setup_with_error")
            raise FixtureSetupError()
            yield FooFixture(*args, **kwargs)
            checkpoints.append("bad.cleanup:NOT_REACHED")

        # -- PERFORM-TEST:
        the_fixture = None
        checkpoints = []
        context = make_runtime_context()
        bad_fixture = bad_with_setup_error
        with pytest.raises(FixtureSetupError):
            with scoped_context_layer(context):
                the_fixture = use_fixture(bad_fixture, context, checkpoints)
                checkpoints.append("scoped-block:NOT_REACHED")

        # -- VERIFY: Ensure normal cleanup-parts were performed.
        # * SAD: fixture-cleanup is not called due to fixture-setup error.
        assert the_fixture is None  # -- NEVER STORED: Due to setup error.
        assert checkpoints == ["bad.setup_with_error"]


    def test_bad_with_setup_error_aborts_on_first_error(self):
        @fixture
        def foo(context, checkpoints, *args, **kwargs):
            fixture_name = kwargs.get("name", "")
            checkpoints.append("foo.setup:%s" % fixture_name)
            yield FooFixture(*args, **kwargs)
            checkpoints.append("foo.cleanup:%s" % fixture_name)

        @fixture
        def bad_with_setup_error(context, checkpoints, *args, **kwargs):
            checkpoints.append("bad.setup_with_error")
            raise FixtureSetupError()
            yield FooFixture(*args, **kwargs)
            checkpoints.append("bad.cleanup:NOT_REACHED")

        # -- PERFORM-TEST:
        the_fixture1 = None
        the_fixture2 = None
        the_fixture3 = None
        checkpoints = []
        context = make_runtime_context()
        bad_fixture = bad_with_setup_error
        with pytest.raises(FixtureSetupError):
            with scoped_context_layer(context):
                the_fixture1 = use_fixture(foo, context, checkpoints, name="foo_1")
                the_fixture2 = use_fixture(bad_fixture, context, checkpoints, name="BAD")
                the_fixture3 = use_fixture(foo, context, checkpoints, name="NOT_REACHED")
                checkpoints.append("scoped-block:NOT_REACHED")

        # -- VERIFY: Ensure cleanup-parts were performed until failure-point.
        assert isinstance(the_fixture1, FooFixture)
        assert the_fixture2 is None     # -- NEVER-STORED:  Due to setup error.
        assert the_fixture3 is None     # -- NEVER-CREATED: Due to bad_fixture.
        assert checkpoints == [
            "foo.setup:foo_1", "bad.setup_with_error", "foo.cleanup:foo_1"]

    def test_bad_with_cleanup_error(self):
        @fixture
        def bad_with_cleanup_error(context, checkpoints, *args, **kwargs):
            checkpoints.append("bad.setup")
            yield FooFixture(*args, **kwargs)
            checkpoints.append("bad.cleanup_with_error")
            raise FixtureCleanupError()

        # -- PERFORM TEST:
        checkpoints = []
        context = make_runtime_context()
        bad_fixture = bad_with_cleanup_error
        with pytest.raises(FixtureCleanupError):
            with scoped_context_layer(context):
                use_fixture(bad_fixture, context, checkpoints)
                checkpoints.append("scoped-block")

        # -- VERIFY: Ensure normal cleanup-parts were performed or tried.
        assert checkpoints == ["bad.setup", "scoped-block", "bad.cleanup_with_error"]

    def test_bad_with_cleanup_error_performs_all_cleanups(self):
        @fixture
        def foo(context, checkpoints, *args, **kwargs):
            fixture_name = kwargs.get("name", "")
            checkpoints.append("foo.setup:%s" % fixture_name)
            yield FooFixture(*args, **kwargs)
            checkpoints.append("foo.cleanup:%s" % fixture_name)

        @fixture
        def bad_with_cleanup_error(context, checkpoints, *args, **kwargs):
            checkpoints.append("bad.setup")
            yield FooFixture(*args, **kwargs)
            checkpoints.append("bad.cleanup_with_error")
            raise FixtureCleanupError()
            checkpoints.append("bad.cleanup.done:NOT_REACHED")

        # -- PERFORM TEST:
        the_fixture1 = None
        the_fixture2 = None
        the_fixture3 = None
        checkpoints = []
        context = make_runtime_context()
        bad_fixture = bad_with_cleanup_error
        with pytest.raises(FixtureCleanupError):
            with scoped_context_layer(context):
                the_fixture1 = use_fixture(foo, context, checkpoints, name="foo_1")
                the_fixture2 = use_fixture(bad_fixture, context, checkpoints, name="BAD")
                the_fixture3 = use_fixture(foo, context, checkpoints, name="foo_3")
                checkpoints.append("scoped-block")

        # -- VERIFY: Tries to perform all cleanups even when cleanup-error(s) occur.
        assert checkpoints == [
            "foo.setup:foo_1", "bad.setup", "foo.setup:foo_3",
            "scoped-block",
            "foo.cleanup:foo_3", "bad.cleanup_with_error", "foo.cleanup:foo_1"]


    def test_bad_with_setup_and_cleanup_error(self):
        # -- GOOD: cleanup_fixture() part is called when setup-error occurs.
        # BUT: FixtureSetupError is hidden by FixtureCleanupError
        @fixture
        def bad_with_setup_and_cleanup_error(context, checkpoints, *args, **kwargs):
            def cleanup_bad_with_error():
                checkpoints.append("bad.cleanup_with_error")
                raise FixtureCleanupError()

            checkpoints.append("bad.setup_with_error")
            context.add_cleanup(cleanup_bad_with_error)
            raise FixtureSetupError()
            return FooFixture("NOT_REACHED")

        # -- PERFORM TEST:
        checkpoints = []
        context = make_runtime_context()
        bad_fixture = bad_with_setup_and_cleanup_error
        with pytest.raises(FixtureCleanupError) as exc_info:
            with scoped_context_layer(context):
                use_fixture(bad_fixture, context, checkpoints, name="BAD2")
                checkpoints.append("scoped-block:NOT_REACHED")

        # -- VERIFY: Ensure normal cleanup-parts were performed or tried.
        # OOPS: FixtureCleanupError in fixture-cleanup hides FixtureSetupError
        assert checkpoints == ["bad.setup_with_error", "bad.cleanup_with_error"]
        assert isinstance(exc_info.value, FixtureCleanupError), "LAST-EXCEPTION-WINS"


class TestUseFixtureByTag(object):
    def test_data_schema1(self):
        @fixture
        def foo(context, *args, **kwargs):
            # -- NOTE checkpoints: Injected from outer scope.
            checkpoints.append("foo.setup")
            yield "fixture:foo"
            checkpoints.append("foo.cleanup")

        fixture_registry = {
            "fixture.foo": foo,
        }

        # -- PERFORM-TEST:
        context = make_runtime_context()
        checkpoints = []
        with scoped_context_layer(context):
            use_fixture_by_tag("fixture.foo", context, fixture_registry)
            checkpoints.append("scoped-block")

        # -- VERIFY:
        assert checkpoints == [
            "foo.setup", "scoped-block", "foo.cleanup"
        ]

    def test_data_schema2(self):
        @fixture
        def foo(context, *args, **kwargs):
            # -- NOTE checkpoints: Injected from outer scope.
            params = "%r, %r" % (args, kwargs)
            checkpoints.append("foo.setup: %s" % params)
            yield "fixture.foo"
            checkpoints.append("foo.cleanup: %s" % params)

        fixture_registry = {
            "fixture.foo": fixture_call_params(foo, 1, 2, 3, name="foo_1")
        }

        # -- PERFORM-TEST:
        context = make_runtime_context()
        checkpoints = []
        with scoped_context_layer(context):
            use_fixture_by_tag("fixture.foo", context, fixture_registry)
            checkpoints.append("scoped-block")

        # -- VERIFY:
        assert checkpoints == [
            "foo.setup: (1, 2, 3), {'name': 'foo_1'}",
            "scoped-block",
            "foo.cleanup: (1, 2, 3), {'name': 'foo_1'}",
        ]

    def test_unknown_fixture_raises_lookup_error(self):
        fixture_registry = {}

        # -- PERFORM-TEST:
        context = make_runtime_context()
        with pytest.raises(LookupError) as exc_info:
            with scoped_context_layer(context):
                use_fixture_by_tag("UNKNOWN_FIXTURE", context, fixture_registry)

        # -- VERIFY:
        assert "Unknown fixture-tag: UNKNOWN_FIXTURE" in str(exc_info.value)

    def test_invalid_data_schema_raises_value_error(self):
        @fixture
        def foo(context, *args, **kwargs):
            pass

        class BadFixtureData(object):
            def __init__(self, fixture_func, *args, **kwargs):
                self.fixture_func = fixture_func
                self.fixture_args = args
                self.fixture_kwargs = kwargs

        fixture_registry = {
            "fixture.foo": BadFixtureData(foo, 1, 2, 3, name="foo_1")
        }

        # -- PERFORM-TEST:
        context = make_runtime_context()
        with pytest.raises(ValueError) as exc_info:
            with scoped_context_layer(context):
                use_fixture_by_tag("fixture.foo", context, fixture_registry)

        # -- VERIFY:
        expected = "fixture_data: Expected tuple or fixture-func, but is:"
        assert expected in str(exc_info.value)
        assert "BadFixtureData object" in str(exc_info.value)


class TestCompositeFixture(object):
    def test_use_fixture(self):
        @fixture
        def fixture_foo(context, checkpoints, *args, **kwargs):
            fixture_name = kwargs.get("name", "foo")
            checkpoints.append("foo.setup:%s" % fixture_name)
            yield
            checkpoints.append("foo.cleanup:%s" % fixture_name)

        @fixture
        def composite2(context, checkpoints, *args, **kwargs):
            the_fixture1 = use_fixture(fixture_foo, context, checkpoints, name="_1")
            the_fixture2 = use_fixture(fixture_foo, context, checkpoints, name="_2")
            return (the_fixture1, the_fixture2)

        # -- PERFORM-TEST:
        context = make_runtime_context()
        checkpoints = []
        with scoped_context_layer(context):
            use_fixture(composite2, context, checkpoints)
            checkpoints.append("scoped-block")

        assert checkpoints == [
            "foo.setup:_1", "foo.setup:_2",
            "scoped-block",
            "foo.cleanup:_2", "foo.cleanup:_1",
        ]

    def test_use_fixture_with_setup_error(self):
        @fixture
        def fixture_foo(context, checkpoints, *args, **kwargs):
            fixture_name = kwargs.get("name", "foo")
            checkpoints.append("foo.setup:%s" % fixture_name)
            yield
            checkpoints.append("foo.cleanup:%s" % fixture_name)

        @fixture
        def bad_with_setup_error(context, checkpoints, *args, **kwargs):
            checkpoints.append("bad.setup_with_error")
            raise FixtureSetupError("OOPS")
            yield
            checkpoints.append("bad.cleanup:NOT_REACHED")

        @fixture
        def composite3(context, checkpoints, *args, **kwargs):
            bad_fixture = bad_with_setup_error
            the_fixture1 = use_fixture(fixture_foo, context, checkpoints, name="_1")
            the_fixture2 = use_fixture(bad_fixture, context, checkpoints, name="OOPS")
            the_fixture3 = use_fixture(fixture_foo, context, checkpoints,
                                       name="_3:NOT_REACHED")
            return (the_fixture1, the_fixture2, the_fixture3) # NOT_REACHED

        # -- PERFORM-TEST:
        context = make_runtime_context()
        checkpoints = []
        with pytest.raises(FixtureSetupError):
            with scoped_context_layer(context):
                use_fixture(composite3, context, checkpoints)
                checkpoints.append("scoped-block:NOT_REACHED")

        # -- ENSURES:
        # * fixture1-cleanup is called even after fixture2-setup-error
        # * fixture3-setup/cleanup are not called due to fixture2-setup-error
        assert checkpoints == [
            "foo.setup:_1", "bad.setup_with_error", "foo.cleanup:_1"
        ]

    def test_use_fixture_with_block_error(self):
        @fixture
        def fixture_foo(context, checkpoints, *args, **kwargs):
            fixture_name = kwargs.get("name", "foo")
            checkpoints.append("foo.setup:%s" % fixture_name)
            yield
            checkpoints.append("foo.cleanup:%s" % fixture_name)

        @fixture
        def composite2(context, checkpoints, *args, **kwargs):
            the_fixture1 = use_fixture(fixture_foo, context, checkpoints, name="_1")
            the_fixture2 = use_fixture(fixture_foo, context, checkpoints, name="_2")
            return (the_fixture1, the_fixture2)

        # -- PERFORM-TEST:
        context = make_runtime_context()
        checkpoints = []
        with pytest.raises(RuntimeError):
            with scoped_context_layer(context):
                use_fixture(composite2, context, checkpoints)
                checkpoints.append("scoped-block_with_error")
                raise RuntimeError("OOPS")
                checkpoints.append("scoped-block.done:NOT_REACHED")

        # -- ENSURES:
        # * fixture1-cleanup/cleanup is called even scoped-block-error
        # * fixture2-cleanup/cleanup is called even scoped-block-error
        # * fixture-cleanup occurs in reversed setup-order
        assert checkpoints == [
            "foo.setup:_1", "foo.setup:_2",
            "scoped-block_with_error",
            "foo.cleanup:_2", "foo.cleanup:_1"
        ]


    def test_use_composite_fixture(self):
        @fixture
        def fixture_foo(context, checkpoints, *args, **kwargs):
            fixture_name = kwargs.get("name", "foo")
            checkpoints.append("foo.setup:%s" % fixture_name)
            yield
            checkpoints.append("foo.cleanup:%s" % fixture_name)

        @fixture
        def composite2(context, checkpoints, *args, **kwargs):
            the_composite = use_composite_fixture_with(context, [
                fixture_call_params(fixture_foo, checkpoints, name="_1"),
                fixture_call_params(fixture_foo, checkpoints, name="_2"),
            ])
            return the_composite

        # -- PERFORM-TEST:
        context = make_runtime_context()
        checkpoints = []
        with scoped_context_layer(context):
            use_fixture(composite2, context, checkpoints)
            checkpoints.append("scoped-block")

        assert checkpoints == [
            "foo.setup:_1", "foo.setup:_2",
            "scoped-block",
            "foo.cleanup:_2", "foo.cleanup:_1",
        ]

    def test_use_composite_fixture_with_setup_error(self):
        @fixture
        def fixture_foo(context, checkpoints, *args, **kwargs):
            fixture_name = kwargs.get("name", "foo")
            checkpoints.append("foo.setup:%s" % fixture_name)
            yield
            checkpoints.append("foo.cleanup:%s" % fixture_name)

        @fixture
        def bad_with_setup_error(context, checkpoints, *args, **kwargs):
            checkpoints.append("bad.setup_with_error")
            raise FixtureSetupError("OOPS")
            yield
            checkpoints.append("bad.cleanup:NOT_REACHED")

        @fixture
        def composite3(context, checkpoints, *args, **kwargs):
            bad_fixture = bad_with_setup_error
            the_composite = use_composite_fixture_with(context, [
                fixture_call_params(fixture_foo, checkpoints, name="_1"),
                fixture_call_params(bad_fixture, checkpoints, name="OOPS"),
                fixture_call_params(fixture_foo, checkpoints, name="_3:NOT_REACHED"),
            ])
            return the_composite

        # -- PERFORM-TEST:
        context = make_runtime_context()
        checkpoints = []
        with pytest.raises(FixtureSetupError):
            with scoped_context_layer(context):
                use_fixture(composite3, context, checkpoints)
                checkpoints.append("scoped-block:NOT_REACHED")

        # -- ENSURES:
        # * fixture1-cleanup is called even after fixture2-setup-error
        # * fixture3-setup/cleanup are not called due to fixture2-setup-error
        assert checkpoints == [
            "foo.setup:_1", "bad.setup_with_error", "foo.cleanup:_1"
        ]

    def test_use_composite_fixture_with_block_error(self):
        @fixture
        def fixture_foo(context, checkpoints, *args, **kwargs):
            fixture_name = kwargs.get("name", "foo")
            checkpoints.append("foo.setup:%s" % fixture_name)
            yield
            checkpoints.append("foo.cleanup:%s" % fixture_name)

        @fixture
        def composite2(context, checkpoints, *args, **kwargs):
            the_composite = use_composite_fixture_with(context, [
                fixture_call_params(fixture_foo, checkpoints, name="_1"),
                fixture_call_params(fixture_foo, checkpoints, name="_2"),
            ])
            return the_composite

        # -- PERFORM-TEST:
        checkpoints = []
        context = make_runtime_context()
        with pytest.raises(RuntimeError):
            with scoped_context_layer(context):
                use_fixture(composite2, context, checkpoints)
                checkpoints.append("scoped-block_with_error")
                raise RuntimeError("OOPS")
                checkpoints.append("scoped-block.done:NOT_REACHED")

        # -- ENSURES:
        # * fixture1-cleanup/cleanup is called even scoped-block-error
        # * fixture2-cleanup/cleanup is called even scoped-block-error
        # * fixture-cleanup occurs in reversed setup-order
        assert checkpoints == [
            "foo.setup:_1", "foo.setup:_2",
            "scoped-block_with_error",
            "foo.cleanup:_2", "foo.cleanup:_1"
        ]

    # -- BAD-EXAMPLE: Ensure SIMPLISTIC-COMPOSITE works as expected
    def test_simplistic_composite_with_setup_error_skips_cleanup(self):
        def setup_bad_fixture_with_error(text):
            raise FixtureSetupError("OOPS")

        @fixture
        def sad_composite2(context, checkpoints, *args, **kwargs):
            checkpoints.append("foo.setup:_1")
            the_fixture1 = FooFixture.setup(*args, **kwargs)
            checkpoints.append("bad.setup_with_error")
            the_fixture2 = setup_bad_fixture_with_error(text="OOPS")
            checkpoints.append("bad.setup.done:NOT_REACHED")
            yield (the_fixture1, the_fixture2)
            checkpoints.append("foo.cleanup:_1:NOT_REACHED")

        # -- PERFORM-TEST:
        context = make_runtime_context()
        checkpoints = []
        with pytest.raises(FixtureSetupError):
            with scoped_context_layer(context):
                use_fixture(sad_composite2, context, checkpoints)
                checkpoints.append("scoped-block:NOT_REACHED")

        # -- VERIFY:
        # * SAD: fixture1-cleanup is not called after fixture2-setup-error
        assert checkpoints == ["foo.setup:_1", "bad.setup_with_error"]

    def test_simplistic_composite_with_block_error_performs_cleanup(self):
        def setup_bad_fixture_with_error(text):
            raise FixtureSetupError("OOPS")

        @fixture
        def simplistic_composite2(context, checkpoints, *args, **kwargs):
            checkpoints.append("foo.setup:_1")
            the_fixture1 = FooFixture.setup(*args, name="_1")
            checkpoints.append("foo.setup:_2")
            the_fixture2 = FooFixture.setup(*args, name="_2")
            yield (the_fixture1, the_fixture2)
            checkpoints.append("foo.cleanup:_1")
            the_fixture1.cleanup()
            checkpoints.append("foo.cleanup:_2")
            the_fixture2.cleanup()

        # -- PERFORM-TEST:
        context = make_runtime_context()
        checkpoints = []
        with pytest.raises(RuntimeError):
            with scoped_context_layer(context):
                use_fixture(simplistic_composite2, context, checkpoints)
                checkpoints.append("scoped-block_with_error")
                raise RuntimeError("OOPS")
                checkpoints.append("scoped-block.end:NOT_REACHED")

        # -- VERIFY:
        # * fixture1-setup/cleanup is called when block-error occurs
        # * fixture2-setup/cleanup is called when block-error occurs
        # * fixture-cleanups occurs in specified composite-cleanup order
        assert checkpoints == [
            "foo.setup:_1", "foo.setup:_2",
            "scoped-block_with_error",
            "foo.cleanup:_1", "foo.cleanup:_2"
        ]


class TestFixtureCleanup(object):
    """Check fixture-cleanup behaviour w/ different fixture implementations."""

    def test_setup_eror_with_plaingen_then_cleanup_is_not_called(self):
        # -- CASE: Fixture is generator-function
        @fixture
        def foo(context, checkpoints):
            checkpoints.append("foo.setup.begin")
            raise FixtureSetupError("foo")
            checkpoints.append("foo.setup.done:NOT_REACHED")
            yield
            checkpoints.append("foo.cleanup:NOT_REACHED")

        checkpoints = []
        context = make_runtime_context()
        with pytest.raises(FixtureSetupError):
            with scoped_context_layer(context):
                use_fixture(foo, context, checkpoints)
                checkpoints.append("scoped-block:NOT_REACHED")

        assert checkpoints == ["foo.setup.begin"]

    def test_setup_eror_with_finallygen_then_cleanup_is_called(self):
        # -- CASE: Fixture is generator-function
        @fixture
        def foo(context, checkpoints):
            try:
                checkpoints.append("foo.setup.begin")
                raise FixtureSetupError("foo")
                checkpoints.append("foo.setup.done:NOT_REACHED")
                yield
                checkpoints.append("foo.cleanup:NOT_REACHED")
            finally:
                checkpoints.append("foo.cleanup.finally")

        checkpoints = []
        context = make_runtime_context()
        with pytest.raises(FixtureSetupError):
            with scoped_context_layer(context):
                use_fixture(foo, context, checkpoints)
                # -- NEVER-REACHED:
                checkpoints.append("scoped-block:NOT_REACHED")

        # -- ENSURE: fixture-cleanup (foo.cleanup) is called (EARLY-CLEANUP).
        assert checkpoints == ["foo.setup.begin", "foo.cleanup.finally"]


    def test_setup_error_with_context_cleanup1_then_cleanup_is_called(self):
        # -- CASE: Fixture is normal function
        @fixture
        def foo(context, checkpoints):
            def cleanup_foo(arg=""):
                checkpoints.append("cleanup_foo:%s" % arg)

            checkpoints.append("foo.setup_with_error:foo_1")
            context.add_cleanup(cleanup_foo, "foo_1")
            raise FixtureSetupError("foo")
            checkpoints.append("foo.setup.done:NOT_REACHED")

        checkpoints = []
        context = make_runtime_context()
        with pytest.raises(FixtureSetupError):
            with scoped_context_layer(context):
                use_fixture(foo, context, checkpoints)
                checkpoints.append("scoped-block:NOT_REACHED")

        # -- ENSURE: cleanup_foo() is called (LATE-CLEANUP on scope-exit)
        assert checkpoints == ["foo.setup_with_error:foo_1", "cleanup_foo:foo_1"]

    def test_setup_error_with_context_cleanup2_then_cleanup_is_called(self):
        # -- CASE: Fixture is generator-function (contextmanager)
        # NOTE: Explicit use of context.add_cleanup()
        @fixture
        def foo(context, checkpoints, **kwargs):
            def cleanup_foo(arg=""):
                checkpoints.append("cleanup_foo:%s" % arg)

            checkpoints.append("foo.setup_with_error:foo_1")
            context.add_cleanup(cleanup_foo, "foo_1")
            raise FixtureSetupError("foo_1")
            checkpoints.append("foo.setup.done:NOT_REACHED")
            yield
            checkpoints.append("foo.cleanup:NOT_REACHED")

        checkpoints = []
        context = make_runtime_context()
        with pytest.raises(FixtureSetupError):
            with scoped_context_layer(context):
                use_fixture(foo, context, checkpoints)
                checkpoints.append("scoped-block:NOT_REACHED")

        # -- ENSURE: cleanup_foo() is called
        assert checkpoints == ["foo.setup_with_error:foo_1", "cleanup_foo:foo_1"]

    def test_block_eror_with_plaingen_then_cleanup_is_called(self):
        # -- CASE: Fixture is generator-function
        @fixture
        def foo(context, checkpoints):
            checkpoints.append("foo.setup")
            yield
            checkpoints.append("foo.cleanup")

        checkpoints = []
        context = make_runtime_context()
        with pytest.raises(RuntimeError):
            with scoped_context_layer(context):
                use_fixture(foo, context, checkpoints)
                checkpoints.append("scoped-block_with_error")
                raise RuntimeError("scoped-block")
                checkpoints.append("NOT_REACHED")

        # -- ENSURE:
        assert checkpoints == [
            "foo.setup", "scoped-block_with_error", "foo.cleanup"
        ]

    def test_block_eror_with_context_cleanup_then_cleanup_is_called(self):
        # -- CASE: Fixture is normal-function
        @fixture
        def bar(context, checkpoints):
            def cleanup_bar():
                checkpoints.append("cleanup_bar")

            checkpoints.append("bar.setup")
            context.add_cleanup(cleanup_bar)

        checkpoints = []
        context = make_runtime_context()
        with pytest.raises(RuntimeError):
            with scoped_context_layer(context):
                use_fixture(bar, context, checkpoints)
                checkpoints.append("scoped-block_with_error")
                raise RuntimeError("scoped-block")
                checkpoints.append("NOT_REACHED")

        # -- ENSURE:
        assert checkpoints == [
            "bar.setup", "scoped-block_with_error", "cleanup_bar"
        ]
