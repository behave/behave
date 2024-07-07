import pytest

from behave.contrib.read_example_table_data_from_csv import read_examples_table_data_from_csv, \
    preprocess_and_read_examples_table_data_from_csv
from behave.model import Feature, ScenarioOutline, Examples


@pytest.fixture
def mock_feature():
    # Create a mock feature with necessary arguments
    feature = Feature(
        filename="mock_feature.feature",  # Replace with appropriate filename
        line=1,  # Replace with appropriate line number
        keyword="Feature",  # Replace with appropriate keyword
        name="Mock Feature"
    )
    return feature


def test_read_examples_table_data_from_csv_existing_file(tmp_path, mock_feature):
    # Create a temporary CSV file
    csv_data = "header1,header2\nvalue1,value2\nvalue3,value4"
    csv_file = tmp_path / "test_file.csv"
    csv_file.write_text(csv_data)

    # Create a scenario outline with examples
    scenario_outline = ScenarioOutline(
        filename=str(csv_file),  # Provide the filename here
        line=2,  # Replace with appropriate line number
        keyword="Scenario Outline",  # Replace with appropriate keyword
        name="Test Scenario Outline"
    )
    examples = Examples(
        filename=str(csv_file),  # Provide the filename here
        line=3,  # Replace with appropriate line number
        keyword="Examples",  # Replace with appropriate keyword
        name="Example set"
    )
    scenario_outline.examples.append(examples)
    mock_feature.scenarios.append(scenario_outline)

    # Mock the example table
    example = mock_feature.scenarios[0].examples[0]

    # Call the function
    read_examples_table_data_from_csv(example, str(csv_file))

    # Assertions
    assert example.table.headings == ["header1", "header2"]
    assert len(example.table.rows) == 2
    assert example.table.rows[0].cells == ["value1", "value2"]
    assert example.table.rows[1].cells == ["value3", "value4"]


def test_preprocess_and_read_examples_table_data_from_csv_existing_file(tmp_path, mock_feature, capsys):
    # Create a temporary CSV file
    csv_data = "header1,header2\nvalue1,value2\nvalue3,value4"
    csv_file = tmp_path / "test1_file.csv"
    csv_file.write_text(csv_data)

    # Mock the feature file
    mock_feature = Feature(
        filename="mock_feature.feature",  # Replace with appropriate filename
        line=1,  # Replace with appropriate line number
        keyword="Feature",  # Replace with appropriate keyword
        name="Mock Feature"
    )

    preprocess_and_read_examples_table_data_from_csv(mock_feature)

    # Capture output and assert file was found
    captured = capsys.readouterr()
    print('Captured', captured.out)

    assert captured.out == '\nFeature filename: mock_feature.feature\n'


def test_read_examples_table_data_from_csv_missing_file(mock_feature):
    # Mock the example table
    example = Examples(
        filename="mock_feature.feature",  # Replace with appropriate filename
        line=3,  # Replace with appropriate line number
        keyword="Examples",  # Replace with appropriate keyword
        name="Example set"
    )
    scenario_outline = ScenarioOutline(
        filename="mock_feature.feature",  # Replace with appropriate filename
        line=2,  # Replace with appropriate line number
        keyword="Scenario Outline",  # Replace with appropriate keyword
        name="Test Scenario Outline"
    )
    scenario_outline.examples.append(example)
    mock_feature.scenarios.append(scenario_outline)

    # Call the function with a non-existent file
    with pytest.raises(FileNotFoundError):
        read_examples_table_data_from_csv(example, "non_existent_file.csv")
