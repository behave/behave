"""
https://github.com/behave/behave/issues/767

When trying to do something like::

    fixture_registry = {'fixture.foo': foo_fixture}
    f = use_fixture_by_tag('fixture.foo', context, fixture_registry)

Behave returns nothing. ::

    repr(f)
    'None'

This seems to be an oversight.
"""

from mock import Mock
from behave.fixture import fixture, use_fixture_by_tag
from behave.runner import Context


def test_issue_767_use_feature_by_tag_has_no_return():
    """Verifies that issue #767 is fixed."""

    @fixture(name='fixture.foo')
    def foo_fixture(context, *args, **kwargs):
        context.foo = 'foo'
        return context.foo

    # -- SCHEMA 1: fixture_func
    fixture_registry1 = {
        "fixture.foo": foo_fixture
    }
    # -- SCHEMA 2: fixture_func, fixture_args, fixture_kwargs
    fixture_registry2 = {
        "fixture.foo": (foo_fixture, (), {})
    }

    context = Context(runner=Mock())
    fixture1 = use_fixture_by_tag("fixture.foo", context, fixture_registry1)
    assert fixture1 == "foo"
    assert context.foo is fixture1

    context = Context(runner=Mock())
    fixture2 = use_fixture_by_tag("fixture.foo", context, fixture_registry2)
    assert fixture2 == "foo"
    assert context.foo is fixture2
