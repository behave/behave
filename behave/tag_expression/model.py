# -*- coding: UTF-8 -*-
# ruff: noqa: F401
# HINT: Import adapter only

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
