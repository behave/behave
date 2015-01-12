# -*- coding: utf-8 -*-
"""
Step definitions for providing notes/hints.
The note steps explain what was important in the last few steps of
this scenario (for a test reader).
"""

from behave import step


# -----------------------------------------------------------------------------
# STEPS FOR: remarks/comments
# -----------------------------------------------------------------------------
@step(u'note that "{remark}"')
def step_note_that(context, remark):
    """
    Used as generic step that provides an additional remark/hint
    and enhance the readability/understanding without performing any check.

    .. code-block:: gherkin

        Given that today is "April 1st"
          But note that "April 1st is Fools day (and beware)"
    """
    log = getattr(context, "log", None)
    if log:
        log.info(u"NOTE: %s;" % remark)

