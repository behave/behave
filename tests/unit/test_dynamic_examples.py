import pytest
import os
import csv
import copy
from unittest.mock import MagicMock, mock_open, patch
from features.environment import load_dynamic_examples_from_csv, before_feature, active_tag_matcher

# Sample data for testing
# Sample data for testing
csv_content = """value1,value2,value3
1,2,3
4,5,6"""


class MockRow:
    def __init__(self, cells):
        self.cells = cells


class MockTable:
    def __init__(self):
        self.rows = [MockRow(cells=['a', 'b', 'c'])]


class MockExample:
    def __init__(self):
        self.table = MockTable()
        self.tags = []


@pytest.fixture
def mock_example():
    return MockExample()


def test_load_dynamic_examples_from_csv(mock_example):
    file_path = os.path.join(os.path.dirname(__file__), '../../tests/unit/test.csv')

    # Mock open to simulate reading csv_content
    with patch('builtins.open', mock_open(read_data=csv_content)):
        load_dynamic_examples_from_csv(mock_example, file_path)

    # Check that the example table rows were updated correctly
    assert len(mock_example.table.rows) == 3
    assert mock_example.table.rows[0].cells == ['value1', 'value2', 'value3']
    assert mock_example.table.rows[1].cells == ['1', '2', '3']
    assert mock_example.table.rows[2].cells == ['4', '5', '6']


def test_load_dynamic_examples_from_csv_file_not_found(mock_example):
    file_path = 'non_existent.csv'

    with pytest.raises(FileNotFoundError, match=f"CSV file not found: {file_path}"):
        load_dynamic_examples_from_csv(mock_example, file_path)


class MockScenario:
    def __init__(self):
        self.examples = []


class MockFeature:
    def __init__(self):
        self.skip = MagicMock()
        self.scenarios = []
        self.tags = []


def test_before_feature_with_exclusion():
    context = MagicMock()
    feature = MockFeature()
    feature.tags = ['exclude']

    with patch.object(active_tag_matcher, 'should_exclude_with', return_value=True), \
        patch.object(active_tag_matcher, 'exclude_reason', "Excluded due to tag"):
        before_feature(context, feature)

        feature.skip.assert_called_once_with(reason="Excluded due to tag")


def test_before_feature_without_exclusion():
    context = MagicMock()
    feature = MockFeature()
    scenario = MockScenario()
    feature.scenarios = [scenario]

    example = MockExample()
    scenario.examples = [example]

    with patch.object(active_tag_matcher, 'should_exclude_with', return_value=False):
        before_feature(context, feature)
        feature.skip.assert_not_called()
