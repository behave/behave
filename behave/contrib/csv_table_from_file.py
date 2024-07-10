# -*- coding: UTF-8 -*-
# pylint: disable=line-too-long
"""
Provides functionality to dynamically populate Examples tables in Behave
feature files from CSV files based on @from_file tags.

EXAMPLE:

.. code-block:: gherkin

    # -- FILE: features/example.feature
    Feature: Example Feature
    Scenario Outline: Example Scenario
        Given get <username> and <email> and <password>
        @from_file=testdata.csv
        Examples:
          | username | email              | password |

        @from_file=testdata2.csv
        Examples:
          | username | email              | password |


.. code-block:: csv

    # -- FILE: testdata.csv
    username,email,password
    user1,email1@example.com,pass1
    user2,email2@example.com,pass2

    # -- FILE: testdata2.csv
    username,email,password
    user3,email3@example.com,pass3
    user4,email4@example.com,pass4

.. code-block:: python

    # -- FILE: features/environment.py
    from behave.contrib.csv_table_from_file import preprocess_and_read_examples_table_data_from_csv

    def before_feature(context, feature):
        preprocess_and_read_examples_table_data_from_csv(feature)
"""

import csv
import logging
import os
from typing import List, Optional

from behave.model import ScenarioOutline, Examples, Table, Feature

logger = logging.getLogger(__name__)


def read_examples_table_data_from_csv(example: Examples, file_path: str) -> None:
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


def select_marker_tag_and_extract_filename(tags: List[str], feature: Feature) -> Optional[str]:
    """
    Helper function to extract the CSV file path from the example's tags and handle relative paths.

    Args:
        tags (List[str]): List of tags associated with the example.
        feature (Feature): The Feature object containing scenarios and scenario outlines.

    Returns:
        Optional[str]: The CSV file path if found in tags, None otherwise.
    """
    for tag in tags:
        if tag.startswith("from_file="):
            csv_file_path = tag.split('=', 1)[1]
            proj_dir = os.path.dirname(os.path.dirname(feature.filename))
            csv_file_path = os.path.join(proj_dir, csv_file_path)
            return csv_file_path
    return None


def preprocess_and_read_examples_table_data_from_csv(feature: Feature) -> None:
    """
    Preprocesses and reads data from CSV files for scenario outlines in the given feature.

    This function processes each scenario outline within the feature, checks for
    an "from_file" tag in the examples table, and if present, reads data from the
    specified CSV file to populate the examples table.

    Args:
        feature (Feature): The Feature object containing scenarios and scenario outlines.

    Raises:
        ValueError: If the CSV file path specified in the tag is not a valid CSV file.
        FileNotFoundError: If the specified CSV file does not exist.
    """
    logger.info(f"Processing feature file: {feature.filename}")

    for scenario in feature.scenarios:
        if isinstance(scenario, ScenarioOutline):
            for example in scenario.examples:
                csv_file_path = select_marker_tag_and_extract_filename(example.tags, feature)

                if not csv_file_path:
                    logger.info(
                        f"No 'from_file' tag found for example table in {feature.filename}, example: {example.name}")
                    continue

                logger.info(f"Loading data from CSV file: {csv_file_path} for example table.")
                try:
                    read_examples_table_data_from_csv(example, csv_file_path)
                    logger.info(f"Successfully loaded data from CSV file: {csv_file_path} for example table.")
                except ValueError as ve:
                    logger.error(str(ve))
                except FileNotFoundError as ve:
                    logger.debug(f"CSV file not found: {csv_file_path}")
