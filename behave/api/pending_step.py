# ruff: noqa: F401
"""
Provides the API needed for pending steps:

* ``StepNotImplementedError`` exception class (preferred)
* ``PendingStepError`` exception class (as alternative)
"""

from __future__ import absolute_import
from behave.exception import StepNotImplementedError, PendingStepError
