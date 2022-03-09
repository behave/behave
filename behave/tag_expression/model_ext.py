# -*- coding: UTF-8 -*-
# pylint: disable=missing-docstring
"""
Extended tag-expression model that supports tag-matchers.

Provides model classes to evaluate parsed boolean tag expressions.

.. code-block:: python

    # -- Expression := a and b
    expression = And(Literal("a"), Literal("b"))
    assert True  == expression.evaluate(["a", "b"])
    assert False == expression.evaluate(["a"])
    assert False == expression.evaluate([])

    # -- Expression := a or b
    expression = Or(Literal("a"), Literal("b"))
    assert True  == expression.evaluate(["a", "b"])
    assert True  == expression.evaluate(["a"])
    assert False == expression.evaluate([])

    # -- Expression := not a
    expression = Not(Literal("a"))
    assert False == expression.evaluate(["a"])
    assert True  == expression.evaluate(["other"])
    assert True  == expression.evaluate([])

    # -- Expression := (a or b) and c
    expression = And(Or(Literal("a"), Literal("b")), Literal("c"))
    assert True  == expression.evaluate(["a", "c"])
    assert False == expression.evaluate(["c", "other"])
    assert False == expression.evaluate([])
"""

from __future__ import absolute_import
from fnmatch import fnmatchcase
import glob
from .model import Expression


# -----------------------------------------------------------------------------
# TAG-EXPRESSION MODEL CLASSES:
# -----------------------------------------------------------------------------
class Matcher(Expression):
    """Matches one or more similar tags by using wildcards.
    Supports simple filename-matching / globbing wildcards only.

    .. code-block:: python

        # -- CASE: Tag starts-with "foo."
        matcher1 = Matcher("foo.*")
        assert True == matcher1.evaluate(["foo.bar"])

        # -- CASE: Tag ends-with ".foo"
        matcher2 = Matcher("*.foo")
        assert True == matcher2.evaluate(["bar.foo"])
        assert True == matcher2.evaluate(["bar.baz_more.foo"])

        # -- CASE: Tag contains "foo"
        matcher3 = Matcher("*.foo.*")
        assert True == matcher3.evaluate(["bar.foo.more"])
        assert True == matcher3.evaluate(["bar.foo"])

    .. see:: :mod:`fnmatch`
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, pattern):
        super(Matcher, self).__init__()
        self.pattern = pattern

    @property
    def name(self):
        return self.pattern

    def evaluate(self, values):
        for value in values:
            # -- REQUIRE: case-sensitive matching
            if fnmatchcase(value, self.pattern):
                return True
        # -- OTHERWISE: no-match
        return False

    def __str__(self):
        return self.pattern

    def __repr__(self):
        return "Matcher('%s')" % self.pattern

    @staticmethod
    def contains_wildcards(text):
        """Indicates if text contains supported wildcards."""
        # -- NOTE: :mod:`glob` wildcards are same as :mod:`fnmatch`
        return glob.has_magic(text)
