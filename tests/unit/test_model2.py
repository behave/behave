# -*- coding: UTF-8 -*-
"""
Additional unit tests for :mod:`behave.model`.
"""

from __future__ import absolute_import, print_function
from behave.model import ScenarioOutlineBuilder, Tag, Row
from behave.model_describe import ModelDescriptor
from behave.textutil import text
from behave.parser import parse_feature, parse_step, parse_tags
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

    @staticmethod
    def assert_make_row_tags(tag_text, expected_tags, params=None):
        if params is None:
            params = {}
        tags = parse_tags(tag_text)
        row = make_row(**params)
        actual_tags = ScenarioOutlineBuilder.make_row_tags(tags, row)
        assert actual_tags == expected_tags

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
Given a simple multi-line text:
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
Given a simple data table:
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
Given a simple data table:
    | Column_1    | Column_2    |
    | Lorem ipsum | Cell_1      |
    | Hello Alice | Ipsum lorem |
'''.strip()

        params = dict(param_1="Cell_1", param_2="Hello", param_3="Alice")
        self.assert_make_step_for_row(step_text, expected_text, params)

    @pytest.mark.parametrize("tag_template,expected", [
        (u"@use.with_category1=<param_1>", u"use.with_category1=PARAM_1"),
        (u"@not.with_category2=<param_2>", u"not.with_category2=PARAM_2"),
    ])
    def test_make_row_tags__with_active_tag_syntax(self, tag_template, expected):
        params = dict(param_1="PARAM_1", param_2="PARAM_2", param_3="UNUSED")
        expected_tags = [expected]
        self.assert_make_row_tags(tag_template, expected_tags, params)

    @pytest.mark.parametrize("tag_template,expected", [
        (u"@tag_1.func(param1=<param_1>,param2=<param_2>)",
         u"tag_1.func(param1=PARAM_1,param2=PARAM_2)")
    ])
    def test_make_row_tags__with_function_like_syntax(self, tag_template, expected):
        tag_template = u"@tag_1.func(param1=<param_1>,param2=<param_2>)"

        params = dict(param_1="PARAM_1", param_2="PARAM_2", param_3="UNUSED")
        expected_tags = [u"tag_1.func(param1=PARAM_1,param2=PARAM_2)"]
        self.assert_make_row_tags(tag_template, expected_tags, params)

    @pytest.mark.parametrize("tag_template,expected", [
        (u"@tag.category1:param1=<param_1>", u"tag.category1:param1=PARAM_1"),
        (u"@tag.category2:param1=<param_1>,param2=<param_2>",
         u"tag.category2:param1=PARAM_1,param2=PARAM_2"),
        (u"@tag.category3:param1=<param_1>;param2=<param_2>",  # SEMICOLON
         u"tag.category3:param1=PARAM_1;param2=PARAM_2"),
    ])
    def test_make_row_tags__with_params_syntax(self, tag_template, expected):
        params = dict(param_1="PARAM_1", param_2="PARAM_2", param_3="UNUSED")
        expected_tags = [expected]
        self.assert_make_row_tags(tag_template, expected_tags, params)

    def test_build_scenarios_with_parametrized_background_steps(self):
        """
        Ensure that placeholders in background steps are supported.

        RELATED TO: Issue #1183
        """
        text = u"""
Feature:
  Background:
    Given a person named "<name>"

  Scenario Outline:
    Then the birth year of this person is "<birth year>"

    Examples:
      | name  | birth year |
      | Alice | 1995 |
      | Bob   | 1985 |
"""
        feature = parse_feature(text)
        expected_step_names = [
            [
                u'a person named "Alice"',
                u'the birth year of this person is "1995"',
            ],
            [
                u'a person named "Bob"',
                u'the birth year of this person is "1985"',
            ],
        ]

        scenarios = list(feature.iter_scenarios())
        assert len(scenarios) == 2

        scenario0_steps = list(scenarios[0].all_steps)
        scenario1_steps = list(scenarios[1].all_steps)
        assert scenario0_steps[0].name == expected_step_names[0][0]
        assert scenario0_steps[1].name == expected_step_names[0][1]
        assert scenario1_steps[0].name == expected_step_names[1][0]
        assert scenario1_steps[1].name == expected_step_names[1][1]

    def test_build_scenarios_with_parameter_row_id(self):
        text = u"""
    Feature:
      @name=<name>
      Scenario Outline: <name> -- row.id=<row.id>
        Then the name of this person is "<name>"

        Examples: Persons
          | name  |
          | Alice |
          | Bob   |

        Examples: Cats
          | name  |
          | Coco |
          | Dubidoo |
    """
        feature = parse_feature(text)
        expected_scenario_names = [
            "Alice -- row.id=1.1 -- @1.1 Persons",
            "Bob -- row.id=1.2 -- @1.2 Persons",
            "Coco -- row.id=2.1 -- @2.1 Cats",
            "Dubidoo -- row.id=2.2 -- @2.2 Cats",
        ]

        scenarios = list(feature.iter_scenarios())
        scenario_names = [scenario.name for scenario in scenarios]
        assert expected_scenario_names == scenario_names

    def test_build_scenarios_with_parameter_row_index(self):
        text = u"""
    Feature:
      @name=<name>
      Scenario Outline: <name> -- row.index=<row.index>
        Then the name of this person is "<name>"

        Examples: Persons
          | name  |
          | Alice |
          | Bob   |

        Examples: Cats
          | name  |
          | Coco |
          | Dubidoo |
    """
        feature = parse_feature(text)
        expected_scenario_names = [
            "Alice -- row.index=1 -- @1.1 Persons",
            "Bob -- row.index=2 -- @1.2 Persons",
            "Coco -- row.index=1 -- @2.1 Cats",
            "Dubidoo -- row.index=2 -- @2.2 Cats",
        ]

        scenarios = list(feature.iter_scenarios())
        scenario_names = [scenario.name for scenario in scenarios]
        assert expected_scenario_names == scenario_names

    def test_build_scenarios_with_parameter_example_name(self):
        text = u"""
    Feature:
      @name=<name>
      Scenario Outline: <name> -- examples.name=<examples.name>
        Then the name of this person is "<name>"

        Examples: Persons
          | name  |
          | Alice |
          | Bob   |

        Examples: Cats
          | name  |
          | Coco |
          | Dubidoo |
    """
        feature = parse_feature(text)
        expected_scenario_names = [
            "Alice -- examples.name=Persons -- @1.1 Persons",
            "Bob -- examples.name=Persons -- @1.2 Persons",
            "Coco -- examples.name=Cats -- @2.1 Cats",
            "Dubidoo -- examples.name=Cats -- @2.2 Cats",
        ]

        scenarios = list(feature.iter_scenarios())
        scenario_names = [scenario.name for scenario in scenarios]
        assert expected_scenario_names == scenario_names

    def test_build_scenarios_with_parameter_example_index(self):
        text = u"""
    Feature:
      @name=<name>
      Scenario Outline: <name> -- examples.index=<examples.index>
        Then the name of this person is "<name>"

        Examples: Persons
          | name  |
          | Alice |
          | Bob   |

        Examples: Cats
          | name  |
          | Coco |
          | Dubidoo |
    """
        feature = parse_feature(text)
        expected_scenario_names = [
            "Alice -- examples.index=1 -- @1.1 Persons",
            "Bob -- examples.index=1 -- @1.2 Persons",
            "Coco -- examples.index=2 -- @2.1 Cats",
            "Dubidoo -- examples.index=2 -- @2.2 Cats",
        ]

        scenarios = list(feature.iter_scenarios())
        scenario_names = [scenario.name for scenario in scenarios]
        assert expected_scenario_names == scenario_names

    def test_build_scenarios_with_parametrized_scenario_tags(self):
        """
        Ensure that placeholders in ScenarioOutline tags are supported.
        """
        text = u"""
    Feature:
      @name=<name>
      Scenario Outline:
        Then the birth year of this person is "<birth year>"

        Examples:
          | name  | birth year |
          | Alice | 1995 |
          | Bob   | 1985 |
    """
        feature = parse_feature(text)
        expected_tags = [
            ["name=Alice"],
            ["name=Bob"],
        ]

        scenarios = list(feature.iter_scenarios())
        assert len(scenarios) == 2

        scenario0_tags = list(scenarios[0].tags)
        scenario1_tags = list(scenarios[1].tags)
        assert scenario0_tags == expected_tags[0]
        assert scenario1_tags == expected_tags[1]

    def test_build_scenarios_with_parametrized_examples_tags(self):
        """
        Ensure that placeholders in Examples tags are supported.

        RELATED TO: Issue #1246, #1240
        """
        text = u"""
Feature:
  Scenario Outline:
    Then the birth year of this person is "<birth year>"

    @name=<name>
    Examples:
      | name  | birth year |
      | Alice | 1995 |
      | Bob   | 1985 |
"""
        feature = parse_feature(text)
        expected_tags = [
            ["name=Alice"],
            ["name=Bob"],
        ]

        scenarios = list(feature.iter_scenarios())
        assert len(scenarios) == 2

        scenario0_tags = list(scenarios[0].tags)
        scenario1_tags = list(scenarios[1].tags)
        assert scenario0_tags == expected_tags[0]
        assert scenario1_tags == expected_tags[1]


class TestTag(object):
    """
    Translation rules are:
      * alnum chars => same, kept
      * space chars => "_"
      * other chars => deleted

    Preserve following characters (in addition to alnums, like: A-z, 0-9):
      * dots        => "." (support: dotted-names, active-tag name schema)
      * minus       => "-" (support: dashed-names)
      * underscore  => "_"
      * equal       => "=" (support: active-tag name schema)
      * colon       => ":" (support: active-tag name schema or similar)
      * semicolon   => ";" (support: complex tag notation)
      * comma       => "," (support: complex tag notation)
      * opening-parens  => "(" (support: complex tag notation)
      * closing-parens  => ")" (support: complex tag notation)
    """
    SAME_AS_TAG = "$SAME_AS_TAG"

    def check_make_name(self, tag, expected):
        if expected is self.SAME_AS_TAG:
            expected = tag

        actual_name = Tag.make_name(tag, allowed_chars=Tag.allowed_chars)
        assert actual_name == expected

    @pytest.mark.parametrize("tag,expected", [
        (u"foo.bar", SAME_AS_TAG),
    ])
    def test_make_name__with_dotted_names(self, tag, expected):
        self.check_make_name(tag, expected)

    @pytest.mark.parametrize("tag,expected", [
        (u"foo-bar", SAME_AS_TAG),
    ])
    def test_make_name__with_dashed_names(self, tag, expected):
        self.check_make_name(tag, expected)

    @pytest.mark.parametrize("tag,expected", [
        (u"foo bar", "foo_bar"),
        (u"foo\tbar", "foo_bar"),
        (u"foo\nbar", "foo_bar"),
    ])
    def test_make_name__spaces_replaced_with_underscore(self, tag, expected):
        self.check_make_name(tag, expected)

    @pytest.mark.parametrize("tag,expected", [
        (u"foo_bar", SAME_AS_TAG),
        (u"foo=bar", SAME_AS_TAG),
        (u"foo:bar", SAME_AS_TAG),
        (u"foo;bar", SAME_AS_TAG),
        (u"foo,bar", SAME_AS_TAG),
        (u"foo(bar=1)", SAME_AS_TAG),
    ])
    def test_make_name__alloweds_char_remain_unmodified(self, tag, expected):
        self.check_make_name(tag, expected)

    @pytest.mark.parametrize("tag,expected", [
        (u"foo<bar>", u"foobar"),
        (u"foo$bar", u"foobar"),
    ])
    def test_make_name__other_chars_are_removed(self, tag, expected):
        self.check_make_name(tag, expected)
