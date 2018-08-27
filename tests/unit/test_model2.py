# -*- coding: UTF-8 -*-
"""
Additional unit tests for :mod:`behave.model`.
"""

from __future__ import absolute_import, print_function
from behave.model import ScenarioOutline, ScenarioOutlineBuilder, Table, Row
from behave.model_describe import ModelDescriptor
from behave.textutil import text
from behave.parser import parse_step
import six
import pytest


# ----------------------------------------------------------------------------
# TEST SUPPORT:
# ----------------------------------------------------------------------------
def make_row(*data, **kwargs):
    line = kwargs.pop("line", None)
    data2 = dict(data, **kwargs)
    headings = list(data2.keys())
    cells = [text(value) for value in data2.values()]
    return Row(headings, cells, line=line)


def step_to_text(step, indentation="    "):
    step_text = u"%s %s" % (step.keyword, step.name)
    more_text = None
    if step.text:
        more_text = ModelDescriptor.describe_docstring(step.text, indentation)
    elif step.table:
        more_text = ModelDescriptor.describe_table(step.table, indentation)
    if more_text:
        step_text = u"%s\n%s" % (step_text, more_text)
    return step_text.rstrip()


# -- PYTEST MARKERS/ANNOTATIONS:
not_implemented_yet = pytest.mark.skip("NOT-IMPLEMENTED-YET")


# ----------------------------------------------------------------------------
# TEST SUITE:
# ----------------------------------------------------------------------------
class TestScenarioOutlineBuilder(object):
    """Unit tests for the templating mechanism that is provided by the
    :class:`behave.model:ScenarioOutlineBuilder`.
    """

    @staticmethod
    def assert_make_step_for_row(step_text, expected_text, params=None):
        if params is None:
            params = {}
        step = parse_step(step_text)
        row = make_row(**params)
        output = ScenarioOutlineBuilder.make_step_for_row(step, row)
        assert step_to_text(output) == expected_text


    def test_make_step_for_row__without_placeholders_remains_unchanged(self):
        step_text = u'Given a step without placeholders'
        expected_text = text(step_text)
        params = dict(firstname="Alice", lastname="Beauville")
        self.assert_make_step_for_row(step_text, expected_text, params)


    def test_make_step_for_row__with_placeholders_in_step(self):
        step_text = u'Given a person with "<firstname> <lastname>"'
        expected_text = u'Given a person with "Alice Beauville"'
        params = dict(firstname="Alice", lastname="Beauville")
        self.assert_make_step_for_row(step_text, expected_text, params)


    def test_make_step_for_row__with_placeholders_in_text(self):
        step_text = u'''\
Given a simple multi-line text:
    """
    <param_1>
    Hello Alice
    <param_2> <param_3>
    __FINI__
    """ 
'''.strip()
        expected_text = u'''\
Given a simple multi-line text
    """
    Param_1
    Hello Alice
    Hello Bob
    __FINI__
    """ 
'''.strip()
        params = dict(param_1="Param_1", param_2="Hello", param_3="Bob")
        self.assert_make_step_for_row(step_text, expected_text, params)


    def test_make_step_for_row__without_placeholders_in_table(self):
        step_text = u'''\
Given a simple data table
    | Column_1 | Column_2 |
    | Lorem ipsum | Ipsum lorem |
'''.strip()
        expected_text = u'''\
Given a simple data table
    | Column_1    | Column_2    |
    | Lorem ipsum | Ipsum lorem |
'''.strip()          # NOTE: Formatting changes whitespace.
        self.assert_make_step_for_row(step_text, expected_text, params=None)


    def test_make_step_for_row__with_placeholders_in_table_headings(self):
        step_text = u'''\
Given a simple data table:
    | <param_1> | Column_2 | <param_2>_<param_3> |
    | Lorem ipsum | 1234   | Ipsum lorem |
'''.strip()
        expected_text = u'''\
Given a simple data table
    | Column_1    | Column_2 | Hello_Column_3 |
    | Lorem ipsum | 1234     | Ipsum lorem    |
'''.strip()
        params = dict(param_1="Column_1", param_2="Hello", param_3="Column_3")
        self.assert_make_step_for_row(step_text, expected_text, params)


    def test_make_step_for_row__with_placeholders_in_table_cells(self):
        step_text = u'''\
Given a simple data table:
    | Column_1 | Column_2 |
    | Lorem ipsum | <param_1> |
    | <param_2> <param_3> | Ipsum lorem |
'''.strip()
        expected_text = u'''\
Given a simple data table
    | Column_1    | Column_2    |
    | Lorem ipsum | Cell_1      |
    | Hello Alice | Ipsum lorem |
'''.strip()

        params = dict(param_1="Cell_1", param_2="Hello", param_3="Alice")
        self.assert_make_step_for_row(step_text, expected_text, params)
