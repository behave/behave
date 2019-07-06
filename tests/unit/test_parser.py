# -*- coding: UTF-8 -*-
# pylint: disable=invalid-name, line-too-long, too-many-lines, bad-whitespace
"""
Unit tests for Gherkin parser: :mod:`behave.parser`.
"""

from __future__ import absolute_import, print_function
import pytest
from behave import i18n, model, parser


# ---------------------------------------------------------------------------
# TEST SUPPORT
# ---------------------------------------------------------------------------
def parse_tags(line):
    the_parser = parser.Parser()
    return the_parser.parse_tags(line.strip())


def assert_compare_steps(steps, expected):
    # OLD: have = [(s.step_type, s.keyword, s.name, s.text, s.table) for s in steps]
    have = [(s.step_type, s.keyword.strip(), s.name, s.text, s.table) for s in steps]
    assert have == expected


# ---------------------------------------------------------------------------
# TEST SUITE
# ---------------------------------------------------------------------------
class TestParser(object):
    # pylint: disable=too-many-public-methods, no-self-use

    def test_parses_feature_name(self):
        feature = parser.parse_feature(u"Feature: Stuff\n")
        assert feature.name == "Stuff"

    def test_parses_feature_name_without_newline(self):
        feature = parser.parse_feature(u"Feature: Stuff")
        assert feature.name == "Stuff"

    def test_parses_feature_description(self):
        doc = u"""
Feature: Stuff
  In order to thing
  As an entity
  I want to do stuff
""".strip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert feature.description == [
            "In order to thing",
            "As an entity",
            "I want to do stuff"
        ]

    def test_parses_feature_with_a_tag(self):
        doc = u"""
@foo
Feature: Stuff
  In order to thing
  As an entity
  I want to do stuff
""".strip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert feature.description == [
            "In order to thing",
            "As an entity",
            "I want to do stuff"
        ]
        assert feature.tags == [model.Tag(u'foo', 1)]

    def test_parses_feature_with_more_tags(self):
        doc = u"""
@foo @bar @baz @qux @winkle_pickers @number8
Feature: Stuff
  In order to thing
  As an entity
  I want to do stuff
""".strip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert feature.description == [
            "In order to thing",
            "As an entity",
            "I want to do stuff"
        ]
        assert feature.tags == [
            model.Tag(name, 1)
            for name in (u'foo', u'bar', u'baz', u'qux', u'winkle_pickers', u'number8')
        ]

    def test_parses_feature_with_a_tag_and_comment(self):
        doc = u"""
@foo    # Comment: ...
Feature: Stuff
  In order to thing
  As an entity
  I want to do stuff
""".strip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert feature.description == [
            "In order to thing",
            "As an entity",
            "I want to do stuff"
        ]
        assert feature.tags, [model.Tag(u'foo', 1)]

    def test_parses_feature_with_more_tags_and_comment(self):
        doc = u"""
@foo @bar @baz @qux @winkle_pickers # Comment: @number8
Feature: Stuff
  In order to thing
  As an entity
  I want to do stuff
""".strip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert feature.description == [
            "In order to thing",
            "As an entity",
            "I want to do stuff"
        ]
        assert feature.tags == [
            model.Tag(name, 1)
            for name in (u'foo', u'bar', u'baz', u'qux', u'winkle_pickers')
        ]
        # -- NOT A TAG: u'number8'

    def test_parses_feature_with_background(self):
        doc = u"""
Feature: Stuff
  Background:
    Given there is stuff
    When I do stuff
    Then stuff happens
""".lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert feature.background
        assert_compare_steps(feature.background.steps, [
            ('given', 'Given', 'there is stuff', None, None),
            ('when', 'When', 'I do stuff', None, None),
            ('then', 'Then', 'stuff happens', None, None),
        ])

    def test_parses_feature_with_description_and_background(self):
        doc = u"""
Feature: Stuff
  This... is... STUFF!

  Background:
    Given there is stuff
    When I do stuff
    Then stuff happens
""".lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert feature.description == ["This... is... STUFF!"]
        assert feature.background
        assert_compare_steps(feature.background.steps, [
            ('given', 'Given', 'there is stuff', None, None),
            ('when', 'When', 'I do stuff', None, None),
            ('then', 'Then', 'stuff happens', None, None),
        ])

    def test_parses_feature_with_a_scenario(self):
        doc = u"""
Feature: Stuff

  Scenario: Doing stuff
    Given there is stuff
    When I do stuff
    Then stuff happens
""".lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name == "Doing stuff"
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'there is stuff', None, None),
            ('when', 'When', 'I do stuff', None, None),
            ('then', 'Then', 'stuff happens', None, None),
        ])

    def test_parses_lowercase_step_keywords(self):
        doc = u"""
Feature: Stuff

  Scenario: Doing stuff
    giVeN there is stuff
    when I do stuff
    tHEn stuff happens
""".lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name == "Doing stuff"
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'there is stuff', None, None),
            ('when', 'When', 'I do stuff', None, None),
            ('then', 'Then', 'stuff happens', None, None),
        ])

    def test_parses_ja_keywords(self):
        doc = u"""
機能: Stuff

  シナリオ: Doing stuff
    前提there is stuff
    もしI do stuff
    ならばstuff happens
""".lstrip()
        feature = parser.parse_feature(doc, language='ja')
        assert feature.name == "Stuff"
        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name, "Doing stuff"
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', u'前提', 'there is stuff', None, None),
            ('when', u'もし', 'I do stuff', None, None),
            ('then', u'ならば', 'stuff happens', None, None),
        ])

    def test_parses_feature_with_description_and_background_and_scenario(self):
        doc = u"""
Feature: Stuff
  Oh my god, it's full of stuff...

  Background:
    Given I found some stuff

  Scenario: Doing stuff
    Given there is stuff
    When I do stuff
    Then stuff happens
""".lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert feature.description == ["Oh my god, it's full of stuff..."]
        assert feature.background
        assert_compare_steps(feature.background.steps, [
            ('given', 'Given', 'I found some stuff', None, None),
        ])

        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name == "Doing stuff"
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'there is stuff', None, None),
            ('when', 'When', 'I do stuff', None, None),
            ('then', 'Then', 'stuff happens', None, None),
        ])

    def test_parses_feature_with_multiple_scenarios(self):
        doc = u"""
Feature: Stuff

  Scenario: Doing stuff
    Given there is stuff
    When I do stuff
    Then stuff happens

  Scenario: Doing other stuff
    When stuff happens
    Then I am stuffed

  Scenario: Doing different stuff
    Given stuff
    Then who gives a stuff
""".lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert len(feature.scenarios) == 3

        assert feature.scenarios[0].name == "Doing stuff"
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'there is stuff', None, None),
            ('when', 'When', 'I do stuff', None, None),
            ('then', 'Then', 'stuff happens', None, None),
        ])

        assert feature.scenarios[1].name == "Doing other stuff"
        assert_compare_steps(feature.scenarios[1].steps, [
            ('when', 'When', 'stuff happens', None, None),
            ('then', 'Then', 'I am stuffed', None, None),
        ])

        assert feature.scenarios[2].name == "Doing different stuff"
        assert_compare_steps(feature.scenarios[2].steps, [
            ('given', 'Given', 'stuff', None, None),
            ('then', 'Then', 'who gives a stuff', None, None),
        ])

    def test_parses_feature_with_multiple_scenarios_with_tags(self):
        doc = u"""
Feature: Stuff

  Scenario: Doing stuff
    Given there is stuff
    When I do stuff
    Then stuff happens

  @one_tag
  Scenario: Doing other stuff
    When stuff happens
    Then I am stuffed

  @lots @of @tags
  Scenario: Doing different stuff
    Given stuff
    Then who gives a stuff
""".lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert len(feature.scenarios) == 3

        assert feature.scenarios[0].name == "Doing stuff"
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'there is stuff', None, None),
            ('when', 'When', 'I do stuff', None, None),
            ('then', 'Then', 'stuff happens', None, None),
        ])

        assert feature.scenarios[1].name == "Doing other stuff"
        assert feature.scenarios[1].tags == [model.Tag(u"one_tag", 1)]
        assert_compare_steps(feature.scenarios[1].steps, [
            ('when', 'When', 'stuff happens', None, None),
            ('then', 'Then', 'I am stuffed', None, None),
        ])

        assert feature.scenarios[2].name == "Doing different stuff"
        assert feature.scenarios[2].tags == [
            model.Tag(n, 1) for n in (u'lots', u'of', u'tags')]
        assert_compare_steps(feature.scenarios[2].steps, [
            ('given', 'Given', 'stuff', None, None),
            ('then', 'Then', 'who gives a stuff', None, None),
        ])

    def test_parses_feature_with_multiple_scenarios_and_other_bits(self):
        doc = u"""
Feature: Stuff
  Stuffing

  Background:
    Given you're all stuffed

  Scenario: Doing stuff
    Given there is stuff
    When I do stuff
    Then stuff happens

  Scenario: Doing other stuff
    When stuff happens
    Then I am stuffed

  Scenario: Doing different stuff
    Given stuff
    Then who gives a stuff
""".lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert feature.description, ["Stuffing"]

        assert feature.background
        assert_compare_steps(feature.background.steps, [
            ('given', 'Given', "you're all stuffed", None, None)
        ])
        assert len(feature.scenarios) == 3

        assert feature.scenarios[0].name == "Doing stuff"
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'there is stuff', None, None),
            ('when', 'When', 'I do stuff', None, None),
            ('then', 'Then', 'stuff happens', None, None),
        ])

        assert feature.scenarios[1].name == "Doing other stuff"
        assert_compare_steps(feature.scenarios[1].steps, [
            ('when', 'When', 'stuff happens', None, None),
            ('then', 'Then', 'I am stuffed', None, None),
        ])

        assert feature.scenarios[2].name == "Doing different stuff"
        assert_compare_steps(feature.scenarios[2].steps, [
            ('given', 'Given', 'stuff', None, None),
            ('then', 'Then', 'who gives a stuff', None, None),
        ])

    def test_parses_feature_with_a_scenario_with_and_and_but(self):
        doc = u"""
Feature: Stuff

  Scenario: Doing stuff
    Given there is stuff
    And some other stuff
    When I do stuff
    Then stuff happens
    But not the bad stuff
""".lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name == "Doing stuff"
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'there is stuff', None, None),
            ('given', 'And', 'some other stuff', None, None),
            ('when', 'When', 'I do stuff', None, None),
            ('then', 'Then', 'stuff happens', None, None),
            ('then', 'But', 'not the bad stuff', None, None),
        ])

    def test_parses_feature_with_a_step_with_a_string_argument(self):
        doc = u'''
Feature: Stuff

  Scenario: Doing stuff
    Given there is stuff:
      """
      So
      Much
      Stuff
      """
    Then stuff happens
'''.lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name == "Doing stuff"
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'there is stuff', "So\nMuch\nStuff", None),
            ('then', 'Then', 'stuff happens', None, None),
        ])

    def test_parses_string_argument_correctly_handle_whitespace(self):
        doc = u'''
Feature: Stuff

  Scenario: Doing stuff
    Given there is stuff:
      """
      So
        Much
          Stuff
        Has
      Indents
      """
    Then stuff happens
'''.lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name == "Doing stuff"
        string = "So\n  Much\n    Stuff\n  Has\nIndents"
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'there is stuff', string, None),
            ('then', 'Then', 'stuff happens', None, None),
        ])

    def test_parses_feature_with_a_step_with_a_string_with_blank_lines(self):
        doc = u'''
Feature: Stuff

  Scenario: Doing stuff
    Given there is stuff:
      """
      So

      Much


      Stuff
      """
    Then stuff happens
'''.lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name == "Doing stuff"
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'there is stuff', "So\n\nMuch\n\n\nStuff", None),
            ('then', 'Then', 'stuff happens', None, None),
        ])

    # MORE-JE-ADDED:
    def test_parses_string_argument_without_stripping_empty_lines(self):
        # -- ISSUE 44: Parser removes comments in multiline text string.
        doc = u'''
Feature: Multiline

  Scenario: Multiline Text with Comments
    Given a multiline argument with:
      """

      """
    And a multiline argument with:
      """
      Alpha.

      Omega.
      """
    Then empty middle lines are not stripped
'''.lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Multiline"
        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name == "Multiline Text with Comments"
        text1 = ""
        text2 = "Alpha.\n\nOmega."
        # pylint: disable=bad-whitespace
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'a multiline argument with', text1, None),
            ('given', 'And',   'a multiline argument with', text2, None),
            ('then', 'Then', 'empty middle lines are not stripped', None, None),
        ])

    def test_parses_feature_with_a_step_with_a_string_with_comments(self):
        doc = u'''
Feature: Stuff

  Scenario: Doing stuff
    Given there is stuff:
      """
      So
      Much
      # Derp
      """
    Then stuff happens
'''.lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name == "Doing stuff"
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'there is stuff', "So\nMuch\n# Derp", None),
            ('then', 'Then', 'stuff happens', None, None),
        ])

    def test_parses_feature_with_a_step_with_a_table_argument(self):
        doc = u'''
Feature: Stuff

  Scenario: Doing stuff
    Given we classify stuff:
      | type of stuff | awesomeness | ridiculousness |
      | fluffy        | large       | frequent       |
      | lint          | low         | high           |
      | green         | variable    | awkward        |
    Then stuff is in buckets
'''.lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name == "Doing stuff"
        table = model.Table(
            [u'type of stuff', u'awesomeness', u'ridiculousness'],
            0,
            [
                [u'fluffy', u'large', u'frequent'],
                [u'lint', u'low', u'high'],
                [u'green', u'variable', u'awkward'],
            ]
        )
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'we classify stuff', None, table),
            ('then', 'Then', 'stuff is in buckets', None, None),
        ])

    @pytest.mark.filterwarnings("ignore:invalid escape sequence")
    def test_parses_feature_with_table_and_escaped_pipe_in_cell_values(self):
        # -- HINT py37: DeprecationWarning: invalid escape sequence '\|'
        # USE: Double escaped-backslashes.
        doc = u'''
Feature:
  Scenario:
    Given we have special cell values:
      | name   | value    |
      | alice  | one\\|two |
      | bob    |\\|one     |
      | charly |     one\\||
      | doro   | one\\|two\\|three\\|four |
'''.lstrip()
        feature = parser.parse_feature(doc)
        assert len(feature.scenarios) == 1
        table = model.Table(
            [u"name", u"value"],
            0,
            [
                [u"alice",  u"one|two"],
                [u"bob",    u"|one"],
                [u"charly", u"one|"],
                [u"doro",   u"one|two|three|four"],
            ]
        )
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'we have special cell values', None, table),
        ])

    def test_parses_feature_with_a_scenario_outline(self):
        doc = u'''
Feature: Stuff

  Scenario Outline: Doing all sorts of stuff
    Given we have <Stuff>
    When we do stuff
    Then we have <Things>

    Examples: Some stuff
      | Stuff      | Things   |
      | wool       | felt     |
      | cotton     | thread   |
      | wood       | paper    |
      | explosives | hilarity |
'''.lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name == "Doing all sorts of stuff"

        table = model.Table(
            [u'Stuff', u'Things'],
            0,
            [
                [u'wool', u'felt'],
                [u'cotton', u'thread'],
                [u'wood', u'paper'],
                [u'explosives', u'hilarity'],
            ]
        )
        assert feature.scenarios[0].examples[0].name == "Some stuff"
        assert feature.scenarios[0].examples[0].table == table
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'we have <Stuff>', None, None),
            ('when', 'When', 'we do stuff', None, None),
            ('then', 'Then', 'we have <Things>', None, None),
        ])

    def test_parses_feature_with_a_scenario_outline_with_multiple_examples(self):
        doc = u'''
Feature: Stuff

  Scenario Outline: Doing all sorts of stuff
    Given we have <Stuff>
    When we do stuff
    Then we have <Things>

    Examples: Some stuff
      | Stuff      | Things   |
      | wool       | felt     |
      | cotton     | thread   |

    Examples: Some other stuff
      | Stuff      | Things   |
      | wood       | paper    |
      | explosives | hilarity |
'''.lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"

        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name == "Doing all sorts of stuff"
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'we have <Stuff>', None, None),
            ('when', 'When', 'we do stuff', None, None),
            ('then', 'Then', 'we have <Things>', None, None),
        ])

        table = model.Table(
            [u'Stuff', u'Things'],
            0,
            [
                [u'wool', u'felt'],
                [u'cotton', u'thread'],
            ]
        )
        assert feature.scenarios[0].examples[0].name == "Some stuff"
        assert feature.scenarios[0].examples[0].table == table

        table = model.Table(
            [u'Stuff', u'Things'],
            0,
            [
                [u'wood', u'paper'],
                [u'explosives', u'hilarity'],
            ]
        )
        assert feature.scenarios[0].examples[1].name == "Some other stuff"
        assert feature.scenarios[0].examples[1].table == table

    def test_parses_feature_with_a_scenario_outline_with_tags(self):
        doc = u'''
Feature: Stuff

  @stuff @derp
  Scenario Outline: Doing all sorts of stuff
    Given we have <Stuff>
    When we do stuff
    Then we have <Things>

    Examples: Some stuff
      | Stuff      | Things   |
      | wool       | felt     |
      | cotton     | thread   |
      | wood       | paper    |
      | explosives | hilarity |
'''.lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"

        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name == "Doing all sorts of stuff"
        assert feature.scenarios[0].tags == [
            model.Tag(u'stuff', 1), model.Tag(u'derp', 1)
        ]
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'we have <Stuff>', None, None),
            ('when', 'When', 'we do stuff', None, None),
            ('then', 'Then', 'we have <Things>', None, None),
        ])

        table = model.Table(
            [u'Stuff', u'Things'],
            0,
            [
                [u'wool', u'felt'],
                [u'cotton', u'thread'],
                [u'wood', u'paper'],
                [u'explosives', u'hilarity'],
            ]
        )
        assert feature.scenarios[0].examples[0].name == "Some stuff"
        assert feature.scenarios[0].examples[0].table == table

    def test_parses_scenario_outline_with_tagged_examples1(self):
        # -- CASE: Examples with 1 tag-line (= 1 tag)
        doc = u'''
Feature: Alice

  @foo
  Scenario Outline: Bob
    Given we have <Stuff>

    @bar
    Examples: Charly
      | Stuff      | Things   |
      | wool       | felt     |
      | cotton     | thread   |
'''.lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Alice"

        assert len(feature.scenarios) == 1
        scenario_outline = feature.scenarios[0]
        assert scenario_outline.name == "Bob"
        assert scenario_outline.tags == [model.Tag(u"foo", 1)]
        assert_compare_steps(scenario_outline.steps, [
            ("given", "Given", "we have <Stuff>", None, None),
        ])

        table = model.Table(
            [u"Stuff", u"Things"], 0,
            [
                [u"wool", u"felt"],
                [u"cotton", u"thread"],
            ]
        )
        assert scenario_outline.examples[0].name == "Charly"
        assert scenario_outline.examples[0].table == table
        assert scenario_outline.examples[0].tags == [model.Tag(u"bar", 1)]

        # -- ScenarioOutline.scenarios:
        # Inherit tags from ScenarioOutline and Examples element.
        assert len(scenario_outline.scenarios) == 2
        expected_tags = [model.Tag(u"foo", 1), model.Tag(u"bar", 1)]
        assert set(scenario_outline.scenarios[0].tags) == set(expected_tags)
        assert set(scenario_outline.scenarios[1].tags), set(expected_tags)

    def test_parses_scenario_outline_with_tagged_examples2(self):
        # -- CASE: Examples with multiple tag-lines (= 2 tag-lines)
        doc = u'''
Feature: Alice

  @foo
  Scenario Outline: Bob
    Given we have <Stuff>

    @bar
    @baz
    Examples: Charly
      | Stuff      | Things   |
      | wool       | felt     |
      | cotton     | thread   |
'''.lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Alice"

        assert len(feature.scenarios) == 1
        scenario_outline = feature.scenarios[0]
        assert scenario_outline.name == "Bob"
        assert scenario_outline.tags == [model.Tag(u"foo", 1)]
        assert_compare_steps(scenario_outline.steps, [
            ("given", "Given", "we have <Stuff>", None, None),
        ])

        table = model.Table(
            [u"Stuff", u"Things"], 0,
            [
                [u"wool", u"felt"],
                [u"cotton", u"thread"],
            ]
        )
        assert scenario_outline.examples[0].name == "Charly"
        assert scenario_outline.examples[0].table == table
        expected_tags = [model.Tag(u"bar", 1), model.Tag(u"baz", 1)]
        assert scenario_outline.examples[0].tags == expected_tags

        # -- ScenarioOutline.scenarios:
        # Inherit tags from ScenarioOutline and Examples element.
        assert len(scenario_outline.scenarios) == 2
        expected_tags = [
            model.Tag(u"foo", 1),
            model.Tag(u"bar", 1),
            model.Tag(u"baz", 1)
        ]
        assert set(scenario_outline.scenarios[0].tags) == set(expected_tags)
        assert set(scenario_outline.scenarios[1].tags), set(expected_tags)

    def test_parses_feature_with_the_lot(self):
        doc = u'''
# This one's got comments too.

@derp
Feature: Stuff
  In order to test my parser
  As a test runner
  I want to run tests

  # A møøse once bit my sister
  Background:
    Given this is a test

  @fred
  Scenario: Testing stuff
    Given we are testing
    And this is only a test
    But this is an important test
    When we test with a multiline string:
      """
      Yarr, my hovercraft be full of stuff.
      Also, I be feelin' this pirate schtick be a mite overdone, me hearties.
          Also: rum.
      """
    Then we want it to work

  #These comments are everywhere man
  Scenario Outline: Gosh this is long
    Given this is <length>
    Then we want it to be <width>
    But not <height>

    Examples: Initial
      | length | width | height |
# I don't know why this one is here
      | 1      | 2     | 3      |
      | 4      | 5     | 6      |

    Examples: Subsequent
      | length | width | height |
      | 7      | 8     | 9      |

  Scenario: This one doesn't have a tag
    Given we don't have a tag
    Then we don't really mind

  @stuff @derp
  Scenario Outline: Doing all sorts of stuff
    Given we have <Stuff>
    When we do stuff with a table:
      | a | b | c | d | e |
      | 1 | 2 | 3 | 4 | 5 |
                             # I can see a comment line from here
      | 6 | 7 | 8 | 9 | 10 |
    Then we have <Things>

    Examples: Some stuff
      | Stuff      | Things   |
      | wool       | felt     |
      | cotton     | thread   |
      | wood       | paper    |
      | explosives | hilarity |
'''.lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Stuff"
        assert feature.tags == [model.Tag(u'derp', 1)]
        assert feature.description == [
            "In order to test my parser",
            "As a test runner",
            "I want to run tests"
        ]

        assert feature.background
        assert_compare_steps(feature.background.steps, [
            ('given', 'Given', 'this is a test', None, None)
        ])

        assert len(feature.scenarios) == 4

        assert feature.scenarios[0].name == 'Testing stuff'
        assert feature.scenarios[0].tags == [model.Tag(u'fred', 1)]
        string = '\n'.join([
            'Yarr, my hovercraft be full of stuff.',
            "Also, I be feelin' this pirate schtick be a mite overdone, " + \
                "me hearties.",
            '    Also: rum.'
        ])
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'we are testing', None, None),
            ('given', 'And', 'this is only a test', None, None),
            ('given', 'But', 'this is an important test', None, None),
            ('when', 'When', 'we test with a multiline string', string, None),
            ('then', 'Then', 'we want it to work', None, None),
        ])

        assert feature.scenarios[1].name == "Gosh this is long"
        assert feature.scenarios[1].tags == []
        table = model.Table(
            [u'length', u'width', u'height'],
            0,
            [
                [u'1', u'2', u'3'],
                [u'4', u'5', u'6'],
            ]
        )
        assert feature.scenarios[1].examples[0].name == "Initial"
        assert feature.scenarios[1].examples[0].table == table
        table = model.Table(
            [u'length', u'width', u'height'],
            0,
            [
                [u'7', u'8', u'9'],
            ]
        )
        assert feature.scenarios[1].examples[1].name == "Subsequent"
        assert feature.scenarios[1].examples[1].table == table
        assert_compare_steps(feature.scenarios[1].steps, [
            ('given', 'Given', 'this is <length>', None, None),
            ('then', 'Then', 'we want it to be <width>', None, None),
            ('then', 'But', 'not <height>', None, None),
        ])

        assert feature.scenarios[2].name == "This one doesn't have a tag"
        assert feature.scenarios[2].tags == []
        assert_compare_steps(feature.scenarios[2].steps, [
            ('given', 'Given', "we don't have a tag", None, None),
            ('then', 'Then', "we don't really mind", None, None),
        ])

        table = model.Table(
            [u'Stuff', u'Things'],
            0,
            [
                [u'wool', u'felt'],
                [u'cotton', u'thread'],
                [u'wood', u'paper'],
                [u'explosives', u'hilarity'],
            ]
        )
        assert feature.scenarios[3].name == "Doing all sorts of stuff"
        assert feature.scenarios[3].tags == [model.Tag(u'stuff', 1), model.Tag(u'derp', 1)]
        assert feature.scenarios[3].examples[0].name == "Some stuff"
        assert feature.scenarios[3].examples[0].table == table
        table = model.Table(
            [u'a', u'b', u'c', u'd', u'e'],
            0,
            [
                [u'1', u'2', u'3', u'4', u'5'],
                [u'6', u'7', u'8', u'9', u'10'],
            ]
        )
        assert_compare_steps(feature.scenarios[3].steps, [
            ('given', 'Given', 'we have <Stuff>', None, None),
            ('when', 'When', 'we do stuff with a table', None, table),
            ('then', 'Then', 'we have <Things>', None, None),
        ])


    def test_fails_to_parse_when_and_is_out_of_order(self):
        text = u"""
Feature: Stuff

  Scenario: Failing at stuff
    And we should fail
""".lstrip()
        with pytest.raises(parser.ParserError):
            parser.parse_feature(text)

    def test_fails_to_parse_when_but_is_out_of_order(self):
        text = u"""
Feature: Stuff

  Scenario: Failing at stuff
    But we shall fail
""".lstrip()
        with pytest.raises(parser.ParserError):
            parser.parse_feature(text)

    def test_fails_to_parse_when_examples_is_in_the_wrong_place(self):
        text = u"""
Feature: Stuff

  Scenario: Failing at stuff
    But we shall fail

    Examples: Failure
      | Fail | Wheel|
""".lstrip()
        with pytest.raises(parser.ParserError):
            parser.parse_feature(text)


class TestForeign(object):
    # pylint: disable=no-self-use

    def test_first_line_comment_sets_language(self):
        doc = u"""
# language: fr
Fonctionnalit\xe9: testing stuff
  Oh my god, it's full of stuff...
"""

        feature = parser.parse_feature(doc)
        assert feature.name == "testing stuff"
        assert feature.description == ["Oh my god, it's full of stuff..."]

    def test_multiple_language_comments(self):
        # -- LAST LANGUAGE is used.
        doc = u"""
# language: en
# language: fr
Fonctionnalit\xe9: testing stuff
  Oh my god, it's full of stuff...
"""

        feature = parser.parse_feature(doc)
        assert feature.name == "testing stuff"
        assert feature.description == ["Oh my god, it's full of stuff..."]

    def test_language_comment_wins_over_commandline(self):
        doc = u"""
# language: fr
Fonctionnalit\xe9: testing stuff
  Oh my god, it's full of stuff...
"""

        feature = parser.parse_feature(doc, language="de")
        assert feature.name == "testing stuff"
        assert feature.description == ["Oh my god, it's full of stuff..."]

    def test_whitespace_before_first_line_comment_still_sets_language(self):
        doc = u"""


# language: cs
Po\u017eadavek: testing stuff
  Oh my god, it's full of stuff...
"""

        feature = parser.parse_feature(doc)
        assert feature.name == "testing stuff"
        assert feature.description == ["Oh my god, it's full of stuff..."]

    def test_anything_before_language_comment_makes_it_not_count(self):
        text = u"""

@wombles
# language: cy-GB
Arwedd: testing stuff
  Oh my god, it's full of stuff...
"""
        with pytest.raises(parser.ParserError):
            parser.parse_feature(text)

    def test_defaults_to_DEFAULT_LANGUAGE(self):
        feature_kwd = i18n.languages[parser.DEFAULT_LANGUAGE]['feature'][0]
        doc = u"""

@wombles
# language: cs
%s: testing stuff
  Oh my god, it's full of stuff...
""" % feature_kwd

        feature = parser.parse_feature(doc)
        assert feature.name == "testing stuff"
        assert feature.description == ["Oh my god, it's full of stuff..."]

    def test_whitespace_in_the_language_comment_is_flexible_1(self):
        doc = u"""
#language:da
Egenskab: testing stuff
  Oh my god, it's full of stuff...
"""

        feature = parser.parse_feature(doc)
        assert feature.name == "testing stuff"
        assert feature.description == ["Oh my god, it's full of stuff..."]

    def test_whitespace_in_the_language_comment_is_flexible_2(self):
        doc = u"""
# language:de
Funktionalit\xe4t: testing stuff
  Oh my god, it's full of stuff...
"""

        feature = parser.parse_feature(doc)
        assert feature.name == "testing stuff"
        assert feature.description == ["Oh my god, it's full of stuff..."]

    def test_whitespace_in_the_language_comment_is_flexible_3(self):
        doc = u"""
#language: en-lol
OH HAI: testing stuff
  Oh my god, it's full of stuff...
"""

        feature = parser.parse_feature(doc)
        assert feature.name == "testing stuff"
        assert feature.description == ["Oh my god, it's full of stuff..."]

    def test_whitespace_in_the_language_comment_is_flexible_4(self):
        doc = u"""
#       language:     lv
F\u012b\u010da: testing stuff
  Oh my god, it's full of stuff...
"""

        feature = parser.parse_feature(doc)
        assert feature.name == "testing stuff"
        assert feature.description == ["Oh my god, it's full of stuff..."]

    def test_parses_french(self):
        doc = u"""
Fonctionnalit\xe9: testing stuff
  Oh my god, it's full of stuff...

  Contexte:
    Soit I found some stuff

  Sc\xe9nario: test stuff
    Soit I am testing stuff
    Alors it should work

  Sc\xe9nario: test more stuff
    Soit I am testing stuff
    Alors it will work
""".lstrip()
        feature = parser.parse_feature(doc, 'fr')
        assert feature.name == "testing stuff"
        assert feature.description == ["Oh my god, it's full of stuff..."]
        assert feature.background
        assert_compare_steps(feature.background.steps, [
            ('given', 'Soit', 'I found some stuff', None, None),
        ])

        assert len(feature.scenarios) == 2
        assert feature.scenarios[0].name == "test stuff"
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Soit', 'I am testing stuff', None, None),
            ('then', 'Alors', 'it should work', None, None),
        ])

    def test_parses_french_multi_word(self):
        doc = u"""
Fonctionnalit\xe9: testing stuff
  Oh my god, it's full of stuff...

  Sc\xe9nario: test stuff
    Etant donn\xe9 I am testing stuff
    Alors it should work
""".lstrip()
        feature = parser.parse_feature(doc, 'fr')
        assert feature.name == "testing stuff"
        assert feature.description == ["Oh my god, it's full of stuff..."]

        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name == "test stuff"
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', u'Etant donn\xe9', 'I am testing stuff', None, None),
            ('then', 'Alors', 'it should work', None, None),
        ])
    test_parses_french_multi_word.go = 1

    def __checkOLD_properly_handles_whitespace_on_keywords_that_do_not_want_it(self):
        doc = u"""
# language: zh-TW

\u529f\u80fd: I have no idea what I'm saying

  \u5834\u666f: No clue whatsoever
    \u5047\u8a2dI've got no idea
    \u7576I say things
    \u800c\u4e14People don't understand
    \u90a3\u9ebcPeople should laugh
    \u4f46\u662fI should take it well
"""

        feature = parser.parse_feature(doc)
        assert feature.name == "I have no idea what I'm saying"

        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name == "No clue whatsoever"
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', u'\u5047\u8a2d', "I've got no idea", None, None),
            ('when', u'\u7576', 'I say things', None, None),
            ('when', u'\u800c\u4e14', "People don't understand", None, None),
            ('then', u'\u90a3\u9ebc', "People should laugh", None, None),
            ('then', u'\u4f46\u662f', "I should take it well", None, None),
        ])

    def test_properly_handles_whitespace_on_keywords_that_do_not_want_it(self):
        data = {'zh-TW': {
            'and': ['*', '假設', '並且', '同時'],
            'background': ['背景'],
            'but': ['*', '但是'],
            'examples': ['例子'],
            'feature': ['功能'],
            'given': ['*', '假如', '假設', '假定'],
            'name': 'Chinese traditional',
            'native': '繁體中文',
            'rule': ['Rule'],
            'scenario': ['場景', '劇本'],
            'scenario_outline': ['場景大綱', '劇本大綱'],
            'then': ['*', '那麼'],
            'when': ['*', '當']
        }}
        doc = u"""
# language: zh-TW

功能: I have no idea what I'm saying

  場景: No clue whatsoever
    假如I've got no idea
    當I say things
    並且People don't understand
    那麼People should laugh
    並且I should take it well
"""

        feature = parser.parse_feature(doc)
        assert feature.name == "I have no idea what I'm saying"

        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name == "No clue whatsoever"
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', u'假如', "I've got no idea", None, None),
            ('when', u'當', 'I say things', None, None),
            ('when', u'並且', "People don't understand", None, None),
            ('then', u'那麼', "People should laugh", None, None),
            ('then', u'並且', "I should take it well", None, None),
        ])


class TestParser4ScenarioDescription(object):
    # pylint: disable=no-self-use

    def test_parse_scenario_description(self):
        doc = u'''
Feature: Scenario Description

  Scenario: With scenario description

    First line of scenario description.
    Second line of scenario description.

    Third line of scenario description (after an empty line).

      Given we have stuff
      When we do stuff
      Then we have things
'''.lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Scenario Description"

        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name == "With scenario description"
        assert feature.scenarios[0].tags == []
        assert feature.scenarios[0].description == [
            "First line of scenario description.",
            "Second line of scenario description.",
            "Third line of scenario description (after an empty line).",
        ]
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'we have stuff', None, None),
            ('when', 'When', 'we do stuff', None, None),
            ('then', 'Then', 'we have things', None, None),
        ])


    def test_parse_scenario_with_description_but_without_steps(self):
        doc = u'''
Feature: Scenario Description

  Scenario: With description but without steps

    First line of scenario description.
    Second line of scenario description.

  Scenario: Another one
      Given we have stuff
      When we do stuff
      Then we have things
'''.lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Scenario Description"

        assert len(feature.scenarios) == 2
        assert feature.scenarios[0].name == "With description but without steps"
        assert feature.scenarios[0].tags == []
        assert feature.scenarios[0].description == [
            "First line of scenario description.",
            "Second line of scenario description.",
        ]
        assert feature.scenarios[0].steps == []

        assert feature.scenarios[1].name == "Another one"
        assert feature.scenarios[1].tags == []
        assert feature.scenarios[1].description == []
        assert_compare_steps(feature.scenarios[1].steps, [
            ('given', 'Given', 'we have stuff', None, None),
            ('when', 'When', 'we do stuff', None, None),
            ('then', 'Then', 'we have things', None, None),
        ])


    def test_parse_scenario_with_description_but_without_steps_followed_by_scenario_with_tags(self):
        doc = u'''
Feature: Scenario Description

  Scenario: With description but without steps

    First line of scenario description.
    Second line of scenario description.

  @foo @bar
  Scenario: Another one
      Given we have stuff
      When we do stuff
      Then we have things
'''.lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Scenario Description"

        assert len(feature.scenarios) == 2
        assert feature.scenarios[0].name == "With description but without steps"
        assert feature.scenarios[0].tags == []
        assert feature.scenarios[0].description == [
            "First line of scenario description.",
            "Second line of scenario description.",
        ]
        assert feature.scenarios[0].steps == []

        assert feature.scenarios[1].name == "Another one"
        assert feature.scenarios[1].tags == ["foo", "bar"]
        assert feature.scenarios[1].description == []
        assert_compare_steps(feature.scenarios[1].steps, [
            ('given', 'Given', 'we have stuff', None, None),
            ('when', 'When', 'we do stuff', None, None),
            ('then', 'Then', 'we have things', None, None),
        ])

    def test_parse_two_scenarios_with_description(self):
        doc = u'''
Feature: Scenario Description

  Scenario: One with description but without steps

    First line of scenario description.
    Second line of scenario description.

  Scenario: Two with description and with steps

    Another line of scenario description.

      Given we have stuff
      When we do stuff
      Then we have things
'''.lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Scenario Description"

        assert len(feature.scenarios) == 2
        assert feature.scenarios[0].name == "One with description but without steps"
        assert feature.scenarios[0].tags == []
        assert feature.scenarios[0].description == [
            "First line of scenario description.",
            "Second line of scenario description.",
        ]
        assert feature.scenarios[0].steps == []

        assert feature.scenarios[1].name == "Two with description and with steps"
        assert feature.scenarios[1].tags == []
        assert feature.scenarios[1].description == [
            "Another line of scenario description.",
        ]
        assert_compare_steps(feature.scenarios[1].steps, [
            ('given', 'Given', 'we have stuff', None, None),
            ('when', 'When', 'we do stuff', None, None),
            ('then', 'Then', 'we have things', None, None),
        ])


class TestParser4Tags(object):
    # pylint: disable=no-self-use

    def test_parse_tags_with_one_tag(self):
        tags = parse_tags('@one  ')
        assert len(tags) == 1
        assert tags[0] == "one"

    def test_parse_tags_with_more_tags(self):
        tags = parse_tags('@one  @two.three-four  @xxx')
        assert len(tags) == 3
        assert tags == [
            model.Tag(name, 1)
            for name in (u'one', u'two.three-four', u'xxx' )
        ]

    def test_parse_tags_with_tag_and_comment(self):
        tags = parse_tags('@one  # @fake-tag-in-comment xxx')
        assert len(tags) == 1
        assert tags[0] == "one"

    def test_parse_tags_with_tags_and_comment(self):
        tags = parse_tags('@one  @two.three-four  @xxx # @fake-tag-in-comment xxx')
        assert len(tags) == 3
        assert tags == [
            model.Tag(name, 1)
            for name in (u'one', u'two.three-four', u'xxx')
        ]

    def test_parse_tags_with_invalid_tags(self):
        with pytest.raises(parser.ParserError):
            parse_tags('@one  invalid.tag boom')


class TestParser4Background(object):
    # pylint: disable=no-self-use

    def test_parse_background(self):
        doc = u'''
Feature: Background

  A feature description line 1.
  A feature description line 2.

  Background: One
    Given we init stuff
    When we init more stuff

  Scenario: One
    Given we have stuff
    When we do stuff
    Then we have things
'''.lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Background"
        assert feature.description == [
            "A feature description line 1.",
            "A feature description line 2.",
        ]
        assert feature.background is not None
        assert feature.background.name == "One"
        assert_compare_steps(feature.background.steps, [
            ('given', 'Given', 'we init stuff', None, None),
            ('when', 'When', 'we init more stuff', None, None),
        ])

        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name == "One"
        assert feature.scenarios[0].tags == []
        assert_compare_steps(feature.scenarios[0].steps, [
            ('given', 'Given', 'we have stuff', None, None),
            ('when', 'When', 'we do stuff', None, None),
            ('then', 'Then', 'we have things', None, None),
        ])

    def test_parse_background_with_description(self):
        # -- RELATED-TO: Issue #713
        doc = u'''
Feature: Background

  A feature description line 1.
  A feature description line 2.

  Background: One
    A background description line 1.
    A background description line 2.

    Given we init stuff
    When we init more stuff

  Scenario: One
'''.lstrip()
        feature = parser.parse_feature(doc)
        assert feature.name == "Background"
        assert feature.description == [
            "A feature description line 1.",
            "A feature description line 2.",
        ]
        assert feature.background is not None
        assert feature.background.name == "One"
        assert feature.background.description == [
            "A background description line 1.",
            "A background description line 2.",
        ]
        assert_compare_steps(feature.background.steps, [
            ('given', 'Given', 'we init stuff', None, None),
            ('when', 'When', 'we init more stuff', None, None),
        ])

        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].name == "One"

    def test_parse_background_with_tags_should_fail(self):
        text = u'''
Feature: Background with tags
  Expect that a ParserError occurs
  because Background does not support tags/tagging.

  @tags_are @not_supported
  @here
  Background: One
    Given we init stuff
'''.lstrip()
        with pytest.raises(parser.ParserError):
            parser.parse_feature(text)


    def test_parse_two_background_should_fail(self):
        text = u'''
Feature: Two Backgrounds
  Expect that a ParserError occurs
  because at most one Background is supported.

  Background: One
    Given we init stuff

  Background: Two
    When we init more stuff
'''.lstrip()
        with pytest.raises(parser.ParserError):
            parser.parse_feature(text)


    def test_parse_background_after_scenario_should_fail(self):
        text = u'''
Feature: Background after Scenario
  Expect that a ParserError occurs
  because Background is only allowed before any Scenario.

  Scenario: One
    Given we have stuff

  Background: Two
    When we init more stuff
'''.lstrip()
        with pytest.raises(parser.ParserError):
            parser.parse_feature(text)


    def test_parse_background_after_scenario_outline_should_fail(self):
        text = u'''
Feature: Background after ScenarioOutline
  Expect that a ParserError occurs
  because Background is only allowed before any ScenarioOuline.
  Scenario Outline: ...
    Given there is <name>

    Examples:
      | name  |
      | Alice |

  Background: Two
    When we init more stuff
'''.lstrip()
        with pytest.raises(parser.ParserError):
            parser.parse_feature(text)


class TestParser4Steps(object):
    """
    Tests parser.parse_steps() and parser.Parser.parse_steps() functionality.
    """
    # pylint: disable=no-self-use

    def test_parse_steps_with_simple_steps(self):
        doc = u'''
Given a simple step
When I have another simple step
 And I have another simple step
Then every step will be parsed without errors
'''.lstrip()
        steps = parser.parse_steps(doc)
        assert len(steps) == 4
        # -- EXPECTED STEP DATA:
        #     SCHEMA: step_type, keyword, name, text, table
        assert_compare_steps(steps, [
            ("given", "Given", "a simple step", None, None),
            ("when",  "When", "I have another simple step", None, None),
            ("when",  "And",  "I have another simple step", None, None),
            ("then",  "Then", "every step will be parsed without errors", None, None),
        ])

    def test_parse_steps_with_multiline_text(self):
        doc = u'''
Given a step with multi-line text:
    """
    Lorem ipsum
    Ipsum lorem
    """
When I have a step with multi-line text:
    """
    Ipsum lorem
    Lorem ipsum
    """
Then every step will be parsed without errors
'''.lstrip()
        steps = parser.parse_steps(doc)
        assert len(steps) == 3
        # -- EXPECTED STEP DATA:
        #     SCHEMA: step_type, keyword, name, text, table
        text1 = "Lorem ipsum\nIpsum lorem"
        text2 = "Ipsum lorem\nLorem ipsum"
        assert_compare_steps(steps, [
            ("given", "Given", "a step with multi-line text", text1, None),
            ("when",  "When",  "I have a step with multi-line text", text2, None),
            ("then",  "Then",  "every step will be parsed without errors",
             None, None),
        ])

    def test_parse_steps_when_last_step_has_multiline_text(self):
        doc = u'''
Given a simple step
Then the last step has multi-line text:
    """
    Lorem ipsum
    Ipsum lorem
    """
'''.lstrip()
        steps = parser.parse_steps(doc)
        assert len(steps) == 2
        # -- EXPECTED STEP DATA:
        #     SCHEMA: step_type, keyword, name, text, table
        text2 = "Lorem ipsum\nIpsum lorem"
        assert_compare_steps(steps, [
            ("given", "Given", "a simple step", None, None),
            ("then",  "Then",  "the last step has multi-line text", text2, None),
        ])

    def test_parse_steps_with_table(self):
        doc = u'''
Given a step with a table:
    | Name  | Age |
    | Alice |  12 |
    | Bob   |  23 |
When I have a step with a table:
    | Country | Capital |
    | France  | Paris   |
    | Germany | Berlin  |
    | Spain   | Madrid  |
    | USA     | Washington |
Then every step will be parsed without errors
'''.lstrip()
        steps = parser.parse_steps(doc)
        assert len(steps) == 3
        # -- EXPECTED STEP DATA:
        #     SCHEMA: step_type, keyword, name, text, table
        table1 = model.Table([u"Name", u"Age"], 0, [
            [ u"Alice", u"12" ],
            [ u"Bob",   u"23" ],
            ])
        table2 = model.Table([u"Country", u"Capital"], 0, [
            [ u"France",   u"Paris" ],
            [ u"Germany",  u"Berlin" ],
            [ u"Spain",    u"Madrid" ],
            [ u"USA",      u"Washington" ],
            ])
        assert_compare_steps(steps, [
            ("given", "Given", "a step with a table", None, table1),
            ("when",  "When",  "I have a step with a table", None, table2),
            ("then",  "Then",  "every step will be parsed without errors",
             None, None),
        ])

    def test_parse_steps_when_last_step_has_a_table(self):
        doc = u'''
Given a simple step
Then the last step has a final table:
    | Name   | City |
    | Alonso | Barcelona |
    | Bred   | London  |
'''.lstrip()
        steps = parser.parse_steps(doc)
        assert len(steps) == 2
        # -- EXPECTED STEP DATA:
        #     SCHEMA: step_type, keyword, name, text, table
        table2 = model.Table([u"Name", u"City"], 0, [
            [ u"Alonso", u"Barcelona" ],
            [ u"Bred",   u"London" ],
            ])
        assert_compare_steps(steps, [
            ("given", "Given", "a simple step", None, None),
            ("then",  "Then",  "the last step has a final table", None, table2),
        ])

    def test_parse_steps_with_malformed_table(self):
        text = u'''
Given a step with a malformed table:
    | Name   | City |
    | Alonso | Barcelona | 2004 |
    | Bred   | London    | 2010 |
'''.lstrip()
        with pytest.raises(parser.ParserError):
            parser.parse_steps(text)
