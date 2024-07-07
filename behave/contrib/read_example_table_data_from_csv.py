import csv
import os
from behave.model import ScenarioOutline
from behave.model import Table


def read_examples_table_data_from_csv(example, file_path):
    """
    Loads examples from the specified CSV file into the given example table.

    Args:
        example: The example table to populate with data from the CSV file.
        file_path: The path to the CSV file containing the example data.

    Raises:
        FileNotFoundError: If the specified CSV file does not exist.
    """

    if os.path.exists(file_path):
        with open(file_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            rows = list(csv_reader)

            if rows:
                # Initialize the table if it doesn't exist
                if example.table is None:
                    example.table = Table(headings=[], rows=[])

                # Use the first row of the CSV as headings if the example table is empty
                if not example.table.headings:
                    example.table.headings = rows[0]

                # Add rows from CSV to example table
                for row in rows[1:]:
                    example.table.add_row(row)
    else:
        raise FileNotFoundError(f'no file found {file_path}')


def preprocess_and_read_examples_table_data_from_csv(feature):
    """
    Preprocesses the feature and loads examples from CSV files for all Scenario Outlines.

    Args:
        feature: The feature to preprocess and populate with example data from CSV files.
    """
    print(f"\nFeature filename: {feature.filename}")
    for scenario in feature.walk_scenarios():
        if isinstance(scenario, ScenarioOutline):

            # Determine the base path for the CSV file
            feature_file_path = feature.filename

            base_path = os.path.splitext(feature_file_path)[0]
            csv_file_path = f"{base_path}.csv"
            # Check if the CSV file exists
            if not os.path.exists(csv_file_path):
                raise FileNotFoundError(f"CSV file not found: {csv_file_path}")

            for example in scenario.examples:
                read_examples_table_data_from_csv(example, csv_file_path)



