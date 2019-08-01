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

def test_issue_767_use_feature_by_tag_has_no_return():
    """Verifies that issue #767 is fixed."""
    from behave.fixture import fixture, use_fixture_by_tag
    from behave.runner import Context

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
    f1 = use_fixture_by_tag('fixture.foo', context, fixture_registry1)
    assert f1 == 'foo'
    assert context.foo is f1

    context = Context(runner=Mock())
    f2 = use_fixture_by_tag('fixture.foo', context, fixture_registry2)
    assert f2 == 'foo'
    assert context.foo is f2
