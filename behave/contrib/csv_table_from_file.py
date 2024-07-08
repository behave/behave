# -*- coding: UTF -*-
# pylint: disable=line-too-long
"""
Provides functionality to dynamically populate Examples tables in Behave
feature files from CSV files based on @from_file tags.

EXAMPLE:

.. sourcecode:: gherkin

    # -- FILE: features/example.feature

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

.. sourcecode:: csv

    # -- FILE: testdata.csv
    username,email,password
    user1,email1@example.com,pass1
    user2,email2@example.com,pass2

    # -- FILE: testdata2.csv
    username,email,password
    user3,email3@example.com,pass3
    user4,email4@example.com,pass4

.. sourcecode:: python

    # -- FILE: features/environment.py
    from behave.contrib.csv_table_from_file import preprocess_and_read_examples_table_data_from_csv

    def before_feature(context, feature):
        preprocess_and_read_examples_table_data_from_csv(feature)

"""

import csv
import os
import logging
from behave.model import Table, Examples, Feature

# Get the logger
logger = logging.getLogger(__name__)


def read_examples_table_data_from_csv(example: Examples, file_path: str):
    """
    Reads data from a CSV file and populates the example's table with the data.

    The CSV file should have a header row matching the example table headings,
    followed by rows of data. This function updates the example's table with
    the data read from the CSV file.

    Args:
        example (Examples): The Examples object to populate with CSV data.
        file_path (str): Path to the CSV file containing data.

    Raises:
        FileNotFoundError: If the specified file_path does not exist.
        ValueError: If the file is not a CSV file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'No file found: {file_path}')

    if not file_path.endswith('.csv'):
        raise ValueError(f'File is not a CSV file: {file_path}')

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


def preprocess_and_read_examples_table_data_from_csv(feature: Feature):
    """
    Preprocesses and reads data from CSV files for scenario outlines in the given feature.

    This function iterates over all scenario outlines in the provided feature,
    looking for Examples tables tagged with @from_file={csv_filename}. For each
    such tag, it reads data from the specified CSV file and populates the Examples
    table with the data.

    Args:
        feature (Feature): The Feature object containing scenario outlines.

    Logs:
        Logs warnings if CSV files for scenario outlines are not found or if the files are not CSV files.
    """
    logger.info(f"Processing feature file: {feature.filename}")
    for scenario_outline in feature.iter_scenario_outlines():
        for example in scenario_outline.examples:
            csv_file_path = None

            # Find the @from_file={csv_filename} tag
            for tag in example.tags:
                if tag.startswith('@from_file='):
                    csv_file_path = tag.split('=', 1)[1]
                    break

            if csv_file_path:
                if not os.path.isabs(csv_file_path):
                    base_path = os.path.dirname(feature.filename)
                    csv_file_path = os.path.join(base_path, csv_file_path)

                try:
                    read_examples_table_data_from_csv(example, csv_file_path)
                    logger.info(f"Loaded data from CSV file: {csv_file_path} for example table.")
                except ValueError as ve:
                    logger.warning(str(ve))
                except FileNotFoundError as ve:
                    logger.warning(str(ve))
            else:
                logger.info(f"No @from_file tag found for example table in {feature.filename}, example: {example.name}")
