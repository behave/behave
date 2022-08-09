"""
https://github.com/behave/behave/issues/1047
"""

from __future__ import absolute_import, print_function
from behave.parser import parse_steps


def test_issue_1047_step_type_for_generic_steps_is_inherited():
    """Verifies that issue #1047 is fixed."""

    text = u"""\
When my step
And my second step
* my third step
"""
    steps = parse_steps(text)
    assert steps[-1].step_type == "when"


def test_issue_1047_step_type_if_only_generic_steps_are_used():
    text = u"""\
* my step
* my another step
"""
    steps = parse_steps(text)
    assert steps[0].step_type == "given"
    assert steps[1].step_type == "given"
