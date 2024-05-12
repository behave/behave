# -*- coding: UTF-8 -*-
# ruff: noqa: F401
# HINT: Import adapter only
"""
Provides TagExpression v2 model classes with some extensions.

Extensions:

* :class:`Matcher` as tag-matcher, like: ``@a.*``

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

    # -- Expression := (a.* or b) and c
    expression = And(Or(Matcher("a.*"), Literal("b")), Literal("c"))
    assert True  == expression.evaluate(["a.one", "c"])
"""

from __future__ import absolute_import, print_function
from fnmatch import fnmatchcase
import glob
# -- INJECT: Cucumber TagExpression model classes
from cucumber_tag_expressions.model import Expression, Literal, And, Or, Not, True_


# -----------------------------------------------------------------------------
# PATCH TAG-EXPRESSION BASE-CLASS: Expression
# -----------------------------------------------------------------------------
def _Expression_check(self, tags):
    """Checks if tags match this tag-expression.
    NOTE: Backward-compatible to tag-expressions v1.

    :param tags:  Tags (as list of strings)
    :return: True, if tag-expression matches tags.
    :return: False, otherwise.
    """
    return self.evaluate(tags)


def _Expression_to_string(self, pretty=True):
    """Provide nicer string conversion(s)."""
    text = str(self)
    if pretty:
        # -- REMOVE WHITESPACE: Around parenthensis
        text = text.replace("( ", "(").replace(" )", ")")
    return text


# -- MONKEY-PATCH:
Expression.check = _Expression_check
Expression.to_string = _Expression_to_string


# -----------------------------------------------------------------------------
# PATCH TAG-EXPRESSION CLASS: Not
# -----------------------------------------------------------------------------
def _Not_to_string(self):
    """Provide nicer/more compact output if Literal(s) are involved."""
    # MAYBE: Literal/True_ need no parenthesis
    schema = "not ( {0} )"
    if isinstance(self.term, (And, Or)):
        # -- REASON: And/Or term have parenthesis already.
        schema = "not {0}"
    return schema.format(self.term)


# -- MONKEY-PATCH:
Not.__str__ = _Not_to_string


# -----------------------------------------------------------------------------
# TAG-EXPRESSION EXTENSION:
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


# -----------------------------------------------------------------------------
# TAG-EXPRESSION EXTENSION:
# -----------------------------------------------------------------------------
class Never(Expression):
    """
    A TagExpression which always returns False.
    """

    def evaluate(self, _values):
        return False

    def __str__(self):
        return "never"

    def __repr__(self):
        return "Never()"
