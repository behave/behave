# -*- coding: UTF-8 -*-
# HINT: PYTHON3 only
# pylint: disable=line-too-long
"""
This module provides a functionality to read the Examples table of a ScenarioOutline
from a CSV file by using ``@from_file={csv_filename}`` tags.

EXAMPLE:

.. code-block:: gherkin

    # -- FILE: features/example.feature
    Feature: Example Feature
      Scenario Outline: Example Scenario
        Given get <username> and <email> and <password>

        @from_file=test_data.csv
        Examples:
          | username | email | password |

        @from_file=some_subdir/test_data2.csv
        Examples:
          | username | email | password |

.. code-block:: python

    # -- FILE: features/environment.py
    from behave.contrib.csv_table_from_file import (
        process_examples_tables_with_marker_tag_and_use_csv_file
    )

    def before_feature(context, feature):
        # -- PROCESS: Any ScenarioOutline.examples[x].table(s)
        process_examples_tables_with_marker_tag_and_use_csv_file(feature)

Using the table data CSV files:

.. code-block:: csv

    # -- TABLE DATA FILE: features/test_data.csv
    username,email,password
    user1,email1@example.com,pass1
    user2,email2@example.com,pass2

.. code-block:: csv

    # -- TABLE DATA FILE: features/some_subdir/test_data2.csv
    username,email,password
    user3,email3@example.com,pass3
    user4,email4@example.com,pass4

LIMITATIONS:

* FileLocation on command line:
  FileLocation mechanism for generated Scenarios of a ScenarioOutline will not work.
  The FileLocation uses the Examples table row "line" in this feature file to refer
  to the corresponding generated Scenario.
"""

import csv
import logging
from pathlib import Path
from typing import List, Optional, Tuple

from behave.model import Feature, Examples


logger = logging.getLogger(__name__)


def select_marker_tag_and_extract_filename(tags: List[str]) -> Optional[str]:
    """
    Extract the CSV filename from the first matching marker-tag.

    * Supports only tags, like: "@from_file=<FILENAME>"
    * Returns only filename for first tag

    :param List[str] tags: List of tags of an Examples object.
    :return: The CSV filename if any is found in tags. None, otherwise.
    :rtype: Optional[str]
    """
    for tag in tags:
        if tag.startswith("from_file="):
            # -- FOUND MARKER-TAG SCHEMA: @from_file={filename}
            filename = tag.split('=', 1)[1]
            return filename

    # -- NOTHING FOUND:
    return None


def select_examples_tables_with_marker_tag(feature: Feature) -> List[Tuple[Examples, str]]:
    """
    Query function to select all Examples with the marker-tag "from_file={filename}".

    :return: Generator of (example, csv_filename) tuples.
    """
    for scenario_template in feature.iter_scenario_outlines():
        for example in scenario_template.examples:
            csv_filename = select_marker_tag_and_extract_filename(example.tags)
            if csv_filename:
                yield (example, csv_filename)


def read_examples_table_data_from_csv(example: Examples, file_path: Path) -> None:
    """
    Reads CSV table data from a CSV file and append it to this example's table.

    The CSV file should have a header row matching the example table headings,
    followed by rows of data. This function updates the example's table with
    the data read from the CSV file.

    NOTE: ``example.table.headings`` define a view on the CSV file data.

    :param Examples example: The Examples object to populate with CSV data.
    :param Path file_path: Path to the CSV file that contains the table data.
    :raises FileNotFoundError: If the specified file_path does not exist.
    :raises ValueError: If the file is not a CSV file.
    """
    if not file_path.exists():
        raise FileNotFoundError(file_path)
    if not file_path.suffix == ".csv":
        raise ValueError(f"{file_path} (expected: CSV file)")
    if not example.table:
        # -- GRACEFULLY IGNORE: Gherkin parser should take care of this.
        # NOTE: example.table.headings are needed as data-view for CSV data.
        return

    column_names = example.table.headings
    with open(file_path, "r") as csv_file:
        # -- USE: csv.DictReader to provide data-view on CSV table data.
        csv_reader = csv.DictReader(csv_file)
        data_rows = list(csv_reader)

        # -- STEP: Add CVS data rows to the table.
        # HINT: Missing CSV data value is None (in BAD-CSV-FILES).
        # MAYBE: Keep track of missing BAD_CSV_TABLE_DATA
        for data_row in data_rows:
            # new_row_data = [(data_row.get(name) or "") for name in column_names]
            new_row_data = []
            for name in column_names:
                cell = data_row.get(name) or ""  # -- ENSURE: string
                new_row_data.append(cell)
            example.table.add_row(new_row_data)


def process_examples_tables_with_marker_tag_and_use_csv_file(feature: Feature,
                                                             strict: bool = False) -> int:
    """
    Processes ScenarioOutlines and their Examples table in this feature.
    If the marker-tag "@from_file={filename}" is present in Examples table tags,
    the CSV table data is read from the CSV file and appended to the Examples table.

    :param Feature feature: The Feature object to be processed.
    :param bool strict: If ``True``, any error will be raised as exception.
    :return:
        * Number of marker-tags found in Examples table tags (if number is positive/zero).
        * Number of processing errors (if number is negative).
    :raises ValueError: If the file is not a CSV file (in strict mode)
    :raises FileNotFoundError: If CSV file does not exist (in strict mode).
    """
    counts = 0
    errors = 0

    def handle_exception(ex):
        nonlocal errors
        nonlocal strict
        message = "{e.__class__.__name__}: {e}"
        logger.error(message)
        errors += 1
        if strict:
            raise

    logger.info(f"PROCESSING: {feature.filename}")
    work_directory = Path(feature.filename).parent

    for example, csv_filename in select_examples_tables_with_marker_tag(feature):
        try:
            counts += 1
            csv_file_path = work_directory/csv_filename
            logger.info(f"Loading table data from CSV file: {csv_file_path}")
            read_examples_table_data_from_csv(example, csv_file_path)
        except ValueError as e:
            handle_exception(e)
        except FileNotFoundError as e:
            handle_exception(e)

    if errors:
        return -errors
    # -- WITHOUT ERRORS:
    return counts
