import pytest
import os
from mock import MagicMock
from behave.model import Examples, Feature, ScenarioOutline, Table
from behave.contrib.csv_table_from_file import (
    read_examples_table_data_from_csv,
    select_marker_tag_and_extract_filename,
    preprocess_and_read_examples_table_data_from_csv,
)


def test_read_examples_table_data_from_csv(tmpdir):
    csv_file = tmpdir.join("test.csv")
    csv_file.write("username,email,password\nuser1,email1,pass1\nuser2,email2,pass2")

    example = Examples("dummy.feature", 1, "Examples", "Example")
    read_examples_table_data_from_csv(example, str(csv_file))

    assert example.table is not None
    assert example.table.headings == ["username", "email", "password"]
    assert example.table.rows[0]['username'] == 'user1'
    assert example.table.rows[0]['email'] == 'email1'
    assert example.table.rows[0]['password'] == 'pass1'


def test_select_marker_tag_and_extract_filename():
    tags = ["from_file=tests/test.csv"]
    feature = MagicMock()
    feature.filename = "/path/to/feature.feature"

    csv_file_path = select_marker_tag_and_extract_filename(tags, feature)

    expected_path = os.path.join(os.path.dirname(os.path.dirname(feature.filename)), "tests/test.csv")
    assert csv_file_path == expected_path


@pytest.fixture
def feature_and_example(tmpdir):
    csv_file = tmpdir.join("test.csv")
    csv_file.write("username,email,password\nuser1,email1,pass1\nuser2,email2,pass2")

    feature_filename = str(tmpdir.join("dummy.feature"))
    feature = Feature(filename=feature_filename, line=1, keyword="Feature", name="Feature")

    example = Examples(filename=feature_filename, line=1, keyword="Examples", name="Example",
                       tags=["from_file=test.csv"])
    scenario_outline = ScenarioOutline(filename=feature_filename, line=1, keyword="Scenario Outline", name="Outline",
                                       examples=[example])

    feature.scenarios = [scenario_outline]

    return feature, example, str(csv_file)


def test_preprocess_and_read_examples_table_data_from_csv(feature_and_example, monkeypatch):
    feature, example, csv_path = feature_and_example

    # Mock the select_marker_tag_and_extract_filename function to return the actual CSV path
    def mock_select_marker(*args, **kwargs):
        return csv_path

    monkeypatch.setattr('behave.contrib.csv_table_from_file.select_marker_tag_and_extract_filename', mock_select_marker)

    preprocess_and_read_examples_table_data_from_csv(feature)

    assert example.table is not None, "Table should not be None"
    assert example.table.headings == ["username", "email", "password"], "Incorrect table headings"
    assert example.table.rows[0]['username'] == 'user1'
    assert example.table.rows[0]['email'] == 'email1'
    assert example.table.rows[0]['password'] == 'pass1'
