# -*- coding: UTF-8 -*-
# pylint: disable=C0209
"""
Common module for tag-expressions:

* v1: old tag expressions (deprecating; superseded by: cucumber-tag-expressions)
* v2: cucumber-tag-expressions (with wildcard extension)

.. seealso::

    * https://docs.cucumber.io
    * https://docs.cucumber.io/cucumber/api/#tag-expressions
"""

from __future__ import absolute_import
from .builder import TagExpressionProtocol, make_tag_expression  # noqa: F401

# -- BACKWARD-COMPATIBLE SUPPORT:
# DEPRECATING: OLD-STYLE TAG-EXPRESSIONS (v1)
from .v1 import TagExpression   # noqa: F401
