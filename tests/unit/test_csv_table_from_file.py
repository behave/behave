import pytest
import os
import csv
from mock import MagicMock, patch
from os.path import dirname, abspath, join
from behave.contrib.csv_table_from_file import read_examples_table_data_from_csv, \
    preprocess_and_read_examples_table_data_from_csv, logger
from behave.model import Table, Feature, Examples


@pytest.fixture
def mock_example():
    mock = MagicMock()
    mock.table = None
    mock.tags = []
    return mock


@pytest.fixture
def mock_feature():
    mock = MagicMock()
    mock.filename = '/path/to/feature.feature'
    return mock


def test_read_examples_table_data_from_csv(mock_example):
    mock_example.table = Table(headings=[], rows=[])
    csv_path = join(dirname(abspath(__file__)), 'test.csv')  # Construct path to test.csv
    read_examples_table_data_from_csv(mock_example, csv_path)
    assert len(mock_example.table.rows) == 2
    assert mock_example.table.headings == ['value1', 'value2', 'value3']
    assert mock_example.table.rows[0]['value1'] == '1'
    assert mock_example.table.rows[0]['value2'] == '2'
    assert mock_example.table.rows[0]['value3'] == '3'


def test_read_examples_table_data_from_csv_nonexistent_file(mock_example):
    with pytest.raises(FileNotFoundError):
        read_examples_table_data_from_csv(mock_example, 'nonexistent.csv')


def test_read_examples_table_data_from_csv_non_csv_file(mock_example):
    with pytest.raises(ValueError):
        read_examples_table_data_from_csv(mock_example, join(dirname(abspath(__file__)), 'not_csv.txt'))


def test_read_examples_table_data_from_csv_empty_file(mock_example):
    empty_csv_path = join(dirname(abspath(__file__)), 'empty.csv')
    with open(empty_csv_path, 'w', newline='') as empty_csv:
        writer = csv.writer(empty_csv)
        writer.writerow([])
    read_examples_table_data_from_csv(mock_example, empty_csv_path)
    assert len(mock_example.table.rows) == 0
    os.remove(empty_csv_path)


@patch('behave.contrib.csv_table_from_file.read_examples_table_data_from_csv')
def test_preprocess_and_read_examples_table_data_from_csv(mock_read_csv, mock_feature):

    mock_scenario_outline = MagicMock()
    mock_examples_with_tag = MagicMock()
    mock_examples_without_tag = MagicMock()

    script_dir = dirname(abspath(__file__))
    csv_filename = 'test.csv'
    mock_examples_with_tag.tags = ['@from_file={}'.format(join(script_dir, csv_filename))]
    mock_examples_without_tag.tags = []

    mock_scenario_outline.examples = [mock_examples_with_tag, mock_examples_without_tag]
    mock_feature.iter_scenario_outlines.return_value = [mock_scenario_outline]

    preprocess_and_read_examples_table_data_from_csv(mock_feature)

    expected_csv_path = join(dirname(abspath(__file__)), 'test.csv')
    mock_read_csv.assert_called_once_with(mock_examples_with_tag, expected_csv_path)
    assert len(mock_read_csv.call_args_list) == 1


def test_preprocess_and_read_examples_table_data_from_csv_nonexistent_csv(mock_feature):
    mock_examples_with_tag = MagicMock()
    mock_examples_with_tag.tags = ['@from_file={}'.format(join(dirname(abspath(__file__)), 'nonexistent.csv'))]
    csv_file_path = join(dirname(abspath(__file__)), 'nonexistent.csv')
    mock_scenario_outline = MagicMock()
    mock_scenario_outline.examples = [mock_examples_with_tag]
    mock_feature.iter_scenario_outlines.return_value = [mock_scenario_outline]

    with patch('behave.contrib.csv_table_from_file.logger.warning') as mock_warning:
        preprocess_and_read_examples_table_data_from_csv(mock_feature)
        mock_warning.assert_called_once_with(f'No file found: {csv_file_path}')
