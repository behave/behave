import pytest
from mock import Mock, patch, mock_open
from behave.model import Feature, ScenarioOutline, Table, Row
import os
import logging

from behave.contrib.csv_table_from_file import read_examples_table_data_from_csv, \
    preprocess_and_read_examples_table_data_from_csv


class Example:
    def __init__(self):
        self.table = None


@pytest.fixture
def mock_feature():
    """
    Fixture that provides a mocked Feature object for testing.

    Returns:
        Mock: Mocked Feature object.
    """
    feature = Mock(spec=Feature)
    feature.filename = 'test.feature'
    return feature


@pytest.fixture
def mock_scenario_outline():
    """
    Fixture that provides a mocked ScenarioOutline object with an example.

    Returns:
        Mock: Mocked ScenarioOutline object.
    """
    scenario_outline = Mock(spec=ScenarioOutline)
    example1 = Example()
    scenario_outline.examples = [example1]
    return scenario_outline


@patch('behave.contrib.csv_table_from_file.open', new_callable=mock_open,
       read_data="column1,column2\ndata1,data2\ndata3,data4")
@patch('behave.contrib.csv_table_from_file.os.path.exists', return_value=True)
def test_read_examples_table_data_from_csv(mock_exists, mock_open):
    """
    Test case for reading examples table data from a CSV file.

    Args:
        mock_exists (MagicMock): Mock for os.path.exists.
        mock_open (MockOpen): Mock for open function with mock_open.

    """
    example = Example()
    example.table = Table(headings=[], rows=[])

    read_examples_table_data_from_csv(example, 'dummy.csv')

    # Construct expected rows using behave's Row objects
    expected_rows = [
        Row(headings=['column1', 'column2'], cells=['data1', 'data2'], line=2),
        Row(headings=['column1', 'column2'], cells=['data3', 'data4'], line=3)
    ]

    assert example.table.headings == ['column1', 'column2']
    assert example.table.rows == expected_rows


@patch('behave.contrib.csv_table_from_file.os.path.exists', return_value=False)
def test_read_examples_table_data_from_csv_file_not_found(mock_exists):
    """
    Test case for handling scenario where the CSV file is not found.

    Args:
        mock_exists (MagicMock): Mock for os.path.exists.
    """
    example = Example()
    with pytest.raises(FileNotFoundError):
        read_examples_table_data_from_csv(example, 'dummy.csv')


@patch('behave.contrib.csv_table_from_file.os.path.exists', return_value=True)
@patch('behave.contrib.csv_table_from_file.read_examples_table_data_from_csv')
def test_preprocess_and_read_examples_table_data_from_csv(mock_read, mock_exists, mock_feature, mock_scenario_outline):
    """
    Test case for preprocessing and reading examples table data from CSV files.

    Args:
        mock_read (MagicMock): Mock for read_examples_table_data_from_csv function.
        mock_exists (MagicMock): Mock for os.path.exists.
        mock_feature (Mock): Mocked Feature object.
        mock_scenario_outline (Mock): Mocked ScenarioOutline object.
    """
    mock_feature.iter_scenario_outlines.return_value = [mock_scenario_outline]

    preprocess_and_read_examples_table_data_from_csv(mock_feature)

    base_path = os.path.splitext(mock_feature.filename)[0]
    csv_file_path = f"{base_path}.csv"

    mock_read.assert_called_with(mock_scenario_outline.examples[0], csv_file_path)


@patch('behave.contrib.csv_table_from_file.os.path.exists', return_value=False)
def test_preprocess_and_read_examples_table_data_from_csv_file_not_found(mock_exists, mock_feature,
                                                                         mock_scenario_outline, caplog):
    """
    Test case for handling scenario where the CSV file is not found during preprocessing.

    Args:
        mock_exists (MagicMock): Mock for os.path.exists.
        mock_feature (Mock): Mocked Feature object.
        mock_scenario_outline (Mock): Mocked ScenarioOutline object.
        caplog (pytest.LogCaptureFixture): Fixture for capturing log messages.
    """
    mock_feature.iter_scenario_outlines.return_value = [mock_scenario_outline]

    with caplog.at_level(logging.WARNING):
        preprocess_and_read_examples_table_data_from_csv(mock_feature)

    assert "CSV file not found" in caplog.text

