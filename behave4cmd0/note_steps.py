# -*- coding: utf-8 -*-
"""
Provides a number of note steps to explain what occurs in this context.

EXAMPLES:

    Given a step passes
    But note that "this a simple example"
"""

from behave import step


# -----------------------------------------------------------------------------
# STEPS FOR: remarks/comments
# -----------------------------------------------------------------------------
@step(u'note that "{remark}"')
def step_note_that(context, remark):
    """
    Used as generic step that provides an additional remark/hint
    without performing any check.

    EXAMPLE:
        Given ...
          But note that "Fools day is April 1st"
    """
    log = getattr(context, "log", None)
    if log:
        log.info(u"NOTE: %s;" % remark)

