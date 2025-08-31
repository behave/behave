# pylint: disable=C0209
"""
Common module for tag-expressions:

* v2: cucumber-tag-expressions (with wildcard extension)

.. seealso::

    * https://docs.cucumber.io
    * https://docs.cucumber.io/cucumber/api/#tag-expressions
"""

from .builder import (
    TagExpressionProtocol,  # noqa: F401
    TagExpressionUtil,      # noqa: F401
    make_tag_expression,    # noqa: F401
)
