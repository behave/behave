# -*- coding: UTF-8 -*-
"""
https://github.com/behave/behave/issues/619

When trying to do something like::

    foo = getattr(context, '_foo', 'bar')

Behave fails with::

    File "[...]/behave/runner.py", line 208, in __getattr__
      return self.__dict__[attr]
    KeyError: '_foo'

I think this is because the __getattr__ method in Context (here) don't raise
properly AttributeError when the key don't exists in the dict,
so the default behaviour of getattr is not executed (see docs).
"""

from __future__ import absolute_import
from behave.runner import Context, scoped_context_layer
from mock import Mock


def test_issue__getattr_with_protected_unknown_context_attribute_raises_no_error():
    context = Context(runner=Mock())
    with scoped_context_layer(context):  # CALLS-HERE: context._push()
        value = getattr(context, "_UNKNOWN_ATTRIB", "__UNKNOWN__")

    assert value == "__UNKNOWN__"
    # -- ENSURED: No exception is raised, neither KeyError nor AttributeError

