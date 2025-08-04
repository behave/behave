"""
Unit tests for :mod:`behave.contrib.csv_table_from_file`.
"""

import pytest
import six
if six.PY2:
    # -- Python2 protection
    pytest.skip("REQUIRES: Python3", allow_module_level=True)


# -----------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------
from collections import OrderedDict
from textwrap import dedent
from behave.contrib.csv_table_from_file import (
    read_examples_table_data_from_csv,
    select_marker_tag_and_extract_filename,
    process_examples_tables_with_marker_tag_and_use_csv_file,
)
from behave.model import Examples, Table
from behave.parser import parse_feature
# DISABLED: from behave.model_describe import ModelDescriptor


# -----------------------------------------------------------------------------
# TEST SUPPORT:
# -----------------------------------------------------------------------------
def ensure_directory_for_file_exists(file_path):
    this_directory = file_path.parent
    if not this_directory.is_dir():
        this_directory.mkdir(parents=True)
    assert this_directory.is_dir()


def table_to_list_of_dicts(table):
    return [row.as_dict() for row in table.rows]


class ExampleBuilder(object):
    DEFAULT_FILENAME = "some.feature"
    DEFAULT_KEYWORD = "Examples"
    DEFAULT_LINE = 10

    @classmethod
    def make_with_table(cls, headings, table_data=None, filename=None, tags=None,
                        **kwargs):
        filename = filename or cls.DEFAULT_FILENAME
        line_number = kwargs.pop("line", cls.DEFAULT_LINE)
        keyword = kwargs.pop("keyword", cls.DEFAULT_KEYWORD)
        name = kwargs.pop("name", "")
        table = Table.from_data(headings, table_data, line=line_number+10)
        return Examples(filename, line=line_number, keyword=keyword, name=name,
                        tags=tags, table=table, **kwargs)


# -----------------------------------------------------------------------------
# TEST DATA:
# -----------------------------------------------------------------------------
CSV_FILE_CONTENTS = dedent("""\
    username,email,password
    Alice,alice@example.me,password_1
    Bob,bob@example.net,password_2
    """)

CSV_FILE_REORDERED_CONTENTS = dedent("""\
    username,password,email
    Alice,password_1,alice@example.me
    Bob,password_2,bob@example.net
    """)

CSV_TABLE_DATA = [
    OrderedDict(username="Alice", email="alice@example.me", password="password_1"),
    OrderedDict(username="Bob", email="bob@example.net", password="password_2"),
]

# -- SYNDROME: Heading row has fewer columns than table data rows -- Additional data is ignored
# EFFECT: Table has fewer columns (2 columns only).
BAD_CSV_FILE_CONTENTS0 = dedent("""\
    username,email
    Alice,alice@example.me,password_1
    Bob,bob@example.net,password_2
    """)

BAD_CSV_TABLE_DATA0 = [
    OrderedDict(username="Alice", email="alice@example.me", password=""),
    OrderedDict(username="Bob", email="bob@example.net", password=""),
]

# -- SYNDROME: First data row has not enough columns
# EFFECT: Table.row1 has fewer cells.
BAD_CSV_FILE_CONTENTS1 = dedent("""\
    username,email,password
    Alice,alice@example.me
    Bob,bob@example.net,password_2
    """)

BAD_CSV_TABLE_DATA1 = [
    OrderedDict(username="Alice", email="alice@example.me", password=""),
    OrderedDict(username="Bob", email="bob@example.net", password="password_2"),
]

# -- SYNDROME: First data row has too many columns
# EFFECT: Additional data is ignored.
BAD_CSV_FILE_CONTENTS2 = dedent("""\
    username,email,password
    Alice,alice@example.me,password_1,__MORE_DATA
    Bob,bob@example.net,password_2
    """)

BAD_CSV_TABLE_DATA2 = CSV_TABLE_DATA


# -----------------------------------------------------------------------------
# TEST SUITE: read_examples_table_data_from_csv
# -----------------------------------------------------------------------------
def test_read_examples_table_data_from_csv__with_valid_csv_file(tmp_path):
    csv_file = tmp_path/"test_data.csv"
    csv_file.write_text(CSV_FILE_CONTENTS)
    assert csv_file.exists()

    headings = ["username", "email", "password"]
    example = ExampleBuilder.make_with_table(headings)
    read_examples_table_data_from_csv(example, csv_file)

    table_data = table_to_list_of_dicts(example.table)
    assert table_data == CSV_TABLE_DATA


def test_read_examples_table_data_from_csv__with_reordered_data_in_csv_file(tmp_path):
    csv_file = tmp_path/"reordered_data.csv"
    csv_file.write_text(CSV_FILE_REORDERED_CONTENTS)
    assert csv_file.exists()

    headings = ["username", "email", "password"]
    example = ExampleBuilder.make_with_table(headings)
    read_examples_table_data_from_csv(example, csv_file)

    table_data = table_to_list_of_dicts(example.table)
    assert table_data == CSV_TABLE_DATA


def test_read_examples_table_data_from_csv__appends_table_data(tmp_path):
    csv_file = tmp_path/"test_data.csv"
    csv_file.write_text(CSV_FILE_CONTENTS)
    assert csv_file.exists()

    headings = ["username", "email", "password"]
    this_table_data = [
        OrderedDict(username="Cerberus", email="cerberus@nowhere.org", password="pass_0"),
    ]
    example = ExampleBuilder.make_with_table(headings, table_data=this_table_data)
    read_examples_table_data_from_csv(example, csv_file)

    table_data = table_to_list_of_dicts(example.table)
    expected = this_table_data + CSV_TABLE_DATA
    assert table_data == expected


def test_read_examples_table_data_from_csv__raises_error_with_missing_file(tmp_path):
    csv_file = tmp_path/"missing.csv"
    assert not csv_file.exists()
    headings = ["username", "email", "password"]
    example = ExampleBuilder.make_with_table(headings)
    with pytest.raises(FileNotFoundError):
        read_examples_table_data_from_csv(example, csv_file)


def test_read_examples_table_data_from_csv__raises_error_with_unsupported_file_format(tmp_path):
    json_file = tmp_path/"test_data.json"
    json_file.write_text("[]")
    assert json_file.exists()

    headings = ["username", "email", "password"]
    example = ExampleBuilder.make_with_table(headings)
    with pytest.raises(ValueError):
        read_examples_table_data_from_csv(example, json_file)


@pytest.mark.parametrize("bad_csv_contents, expected", [
    (BAD_CSV_FILE_CONTENTS0, BAD_CSV_TABLE_DATA0),
    (BAD_CSV_FILE_CONTENTS1, BAD_CSV_TABLE_DATA1),
    (BAD_CSV_FILE_CONTENTS2, CSV_TABLE_DATA)
])
def test_read_examples_table_data_from_csv__raises_error_with_bad_csv_file(bad_csv_contents,
                                                                           expected,
                                                                           tmp_path):
    csv_file = tmp_path/"bad_data.csv"
    csv_file.write_text(bad_csv_contents)

    headings = ["username", "email", "password"]
    example = ExampleBuilder.make_with_table(headings)
    read_examples_table_data_from_csv(example, csv_file)

    table_data = table_to_list_of_dicts(example.table)
    assert table_data == expected


def test_read_examples_table_data_from_csv__raises_error_if_file_is_not_found(tmp_path):
    csv_file = tmp_path/"MISSING.csv"
    assert not csv_file.exists()

    headings = ["username", "email", "password"]
    example = ExampleBuilder.make_with_table(headings)
    with pytest.raises(FileNotFoundError):
        read_examples_table_data_from_csv(example, csv_file)


def test_read_examples_table_data_from_csv__raises_error_with_non_csv_file(tmp_path):
    other_file = tmp_path/"test_data.json"
    other_file.write_text("[]")
    assert other_file.exists()

    # example = Examples(str(tmp_path/"some.feature"), 10, "Examples", "From CSV File")
    headings = ["username", "email", "password"]
    example = ExampleBuilder.make_with_table(headings)
    with pytest.raises(ValueError):
        read_examples_table_data_from_csv(example, other_file)


# -----------------------------------------------------------------------------
# TESTS FOR: select_marker_tag_and_extract_filename
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("tags, expected", [
    (["from_file=test_data.csv"], "test_data.csv"),
    (["from_file=test_data1.csv", "from_file=test_data2.csv"], "test_data1.csv"),
])
def test_select_marker_tag_and_extract_filename(tags, expected):
    csv_file_path = select_marker_tag_and_extract_filename(tags)
    assert csv_file_path == expected


@pytest.mark.parametrize("tags, case", [
    ([], "case: No tags"),
    (["foo"], "case: Other tag"),
    (["foo", "bar"], "case: Other tags"),
    (["from_file1=test_data.csv"], "case: Similar tag1"),
    (["from_file:test_data.csv"], "case: Similar tag2"),
])
def test_select_marker_tag_and_extract_filename__without_matching_tag_returns_none(tags, case):
    csv_file_path = select_marker_tag_and_extract_filename(tags)
    assert csv_file_path is None


# -----------------------------------------------------------------------------
# TESTS FOR: process_examples_tables_with_marker_tag_and_use_csv_file
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("csv_filename", [
    "test_data.csv",
    "subdir/test_data.csv",
])
def test_process_examples_tables_with_marker_tag__good_case(csv_filename, tmp_path):
    text = dedent("""
        Feature:
          Scenario Outline:
            Given person login with username="<username>"

            @from_file={csv_filename}
            Examples:
              | username | email | password |
        """.format(csv_filename=csv_filename))
    feature_path = tmp_path/"some.feature"
    csv_file_path = tmp_path/csv_filename
    ensure_directory_for_file_exists(csv_file_path)
    csv_file_path.write_text(CSV_FILE_CONTENTS)

    # -- ACT:
    feature = parse_feature(text, filename=str(feature_path))
    counts = process_examples_tables_with_marker_tag_and_use_csv_file(feature)

    # -- ASSERT:
    scenario_outlines = list(feature.iter_scenario_outlines())
    assert len(scenario_outlines) == 1
    this_scenario_outline = scenario_outlines[0]
    this_example = this_scenario_outline.examples[0]
    this_table_data = table_to_list_of_dicts(this_example.table)
    assert this_table_data == CSV_TABLE_DATA
    assert counts == 1

#     table_text = ModelDescriptor.describe_table(example.table).rstrip()
#     expected = """
# | username | email            | password   |
# | Alice    | alice@example.me | password_1 |
# | Bob      | bob@example.net  | password_2 |
# """.strip()
#     assert table_text == expected


@pytest.mark.parametrize("csv_filename", ["test_data.csv"])
def test_process_examples_tables_with_marker_tag__causes_rebuild_scenarios(csv_filename, tmp_path):
    """
    Ensure that the new, extended ScenarioOutline.example.table data
    causes that its ScenarioOutline.scenarios are rebuild/regenerated.
    """
    text = dedent("""
        Feature:
          Scenario Outline:
            Given person login with username="<username>"

            @from_file={csv_filename}
            Examples:
              | username | email                | password |
              | Cerberus | cerberus@nowhere.org | pass_0   |
        """.format(csv_filename=csv_filename))
    feature_path = tmp_path/"some.feature"
    csv_file_path = tmp_path/csv_filename
    ensure_directory_for_file_exists(csv_file_path)
    csv_file_path.write_text(CSV_FILE_CONTENTS)
    initial_table_data = [
        OrderedDict(username="Cerberus", email="cerberus@nowhere.org", password="pass_0"),
    ]

    # -- ACT:
    feature = parse_feature(text, filename=str(feature_path))
    scenario_outlines = list(feature.iter_scenario_outlines())
    this_scenario_outline = scenario_outlines[0]
    this_initial_scenarios = this_scenario_outline.scenarios  # ENSURE: precomputed.
    process_examples_tables_with_marker_tag_and_use_csv_file(feature)

    # -- ASSERT:
    assert len(this_initial_scenarios) == 1
    this_example = this_scenario_outline.examples[0]
    this_table_data = table_to_list_of_dicts(this_example.table)
    expected = initial_table_data + CSV_TABLE_DATA
    assert this_table_data == expected

    # -- CHECK: New, extended example.table data regenerates scenarios.
    assert len(this_scenario_outline.scenarios) == len(this_table_data)
    assert len(this_scenario_outline.scenarios) > 0
    assert len(this_initial_scenarios) < len(this_scenario_outline.scenarios)
