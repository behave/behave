# -*- coding: UTF-8 -*-
# HINT: Import adapter only

from cucumber_tag_expressions.model import Expression, Literal, And, Or, Not

# -----------------------------------------------------------------------------
# PATCH TAG-EXPRESSION BASE-CLASS:
# -----------------------------------------------------------------------------
def _Expression_check(self, tags):
    """Checks if tags match this tag-expression.
    NOTE: Backward-compatible to tag-expressions v1.

    :param tags:  Tags (as list of strings)
    :return: True, if tag-expression matches tags.
    :return: False, otherwise.
    """
    return self.evaluate(tags)


Expression.check = _Expression_check
