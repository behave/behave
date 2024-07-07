import logging
import csv
import os
from behave.model import Table, ScenarioOutline

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_examples_table_data_from_csv(example, file_path):
    """
    Reads data from a CSV file and populates the example's table with the data.

    Args:
        example (behave.model.Examples): The Examples object to populate with CSV data.
        file_path (str): Path to the CSV file containing data.

    Raises:
        FileNotFoundError: If the specified file_path does not exist.

    Example:
        Feature: Example Feature

        Scenario Outline: Example Scenario
            Given get <username> and <email> and <password>

            @from_file=testdata.csv
            Examples:
              | username | email   | password |
              | .        | .       | .        |

            @from_file=testdata2.csv
            Examples:
              | username | email   | password |
              | .        | .       | .        |
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'No file found: {file_path}')

    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        rows = list(csv_reader)

        if rows:
            if example.table is None:
                example.table = Table(headings=[], rows=[])

            if not example.table.headings:
                example.table.headings = rows[0]

            for row in rows[1:]:
                example.table.add_row(row)


def preprocess_and_read_examples_table_data_from_csv(feature):
    """
    Preprocesses and reads data from CSV files for scenario outlines in the given feature.

    Args:
        feature (behave.model.Feature): The Feature object containing scenario outlines.

    Logs:
        Logs warnings if CSV files for scenario outlines are not found.
    """
    logger.info(f"Feature filename: {feature.filename}")
    for scenario_outline in feature.iter_scenario_outlines():
        base_path = os.path.splitext(feature.filename)[0]
        csv_file_path = f"{base_path}.csv"

        if not os.path.exists(csv_file_path):
            logger.warning(f"CSV file not found: {csv_file_path}")
            continue

        for example in scenario_outline.examples:
            read_examples_table_data_from_csv(example, csv_file_path)

