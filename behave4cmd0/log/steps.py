# -*- coding: utf-8 -*-
"""
Provides step definitions to perform tests with the Python logging subsystem.

.. code-block: gherkin

    Given I create log records with:
        | category | level   | message |
        | foo.bar  | WARN    | Hello LogRecord |
        | bar      | CURRENT | Hello LogRecord |
    And I create a log record with:
        | category | level   | message |
        | foo      | ERROR   | Hello Foo |
    Then the command output should contain the following log records:
        | category | level   | message |
        | bar      | CURRENT | xxx     |
    Then the command output should not contain the following log records:
        | category | level   | message |
        | bar      | CURRENT | xxx     |
    Then the file "behave.log" should contain the log records:
        | category | level   | message |
        | bar      | CURRENT | xxx     |
    Then the file "behave.log" should not contain the log records:
        | category | level   | message |
        | bar      | CURRENT | xxx     |

    Given I define the log record schema:
        | category | level   | message |
        | root     | INFO    | Hello LogRecord |
    And I create log records with:
        | category | level   | message |
        | foo.bar  | INFO    | Hello LogRecord |
        | bar      | INFO    | Hello LogRecord |
    Then the command output should contain log records from categories
        | category |
        | foo.bar  |
        | bar      |

    Given I use the log record configuration:
        | property | value |
        | format   | LOG.%(levelname)-8s %(name)s %(message)s |
        | datefmt  |       |

IDEA:

.. code-block:: gherkin

    Given I capture log records
    When I create log records with:
        | category | level   | message |
        | foo.bar  | WARN    | Hello LogRecord |
    Then the captured log should contain the following log records:
        | category | level   | message |
        | bar      | CURRENT | xxx     |
    And the captured log should not contain the following log records:
        | category | level   | message |
        | bar      | CURRENT | xxx     |
"""

from __future__ import absolute_import
from behave import given, when, then, step
from behave4cmd0.command_steps import \
    step_file_should_contain_multiline_text, \
    step_file_should_not_contain_multiline_text
from behave.configuration import LogLevel
from behave.log_capture import LoggingCapture
import logging

# -----------------------------------------------------------------------------
# STEP UTILS:
# -----------------------------------------------------------------------------
def make_log_record(category, level, message):
    if category in ("root", "__ROOT__"):
        category = None
    logger = logging.getLogger(category)
    logger.log(level, message)

def make_log_record_output(category, level, message,
                           format=None, datefmt=None, **kwargs):
    """
    Create the output for a log record, like performed by :mod:`logging` module.

    :param category:    Name of the logger (as string or None).
    :param level:       Log level (as number).
    :param message:     Log message to use.
    :returns: Log record output (as string)
    """
    if not category or (category == "__ROOT__"):
        category = "root"
    levelname = logging.getLevelName(level)
    record_data = dict(name=category, levelname=levelname, msg=message)
    record_data.update(kwargs)
    record = logging.makeLogRecord(record_data)
    formatter = logging.Formatter(format, datefmt=datefmt)
    return formatter.format(record)

class LogRecordTable(object):

    @classmethod
    def make_output_for_row(cls, row, format=None, datefmt=None, **kwargs):
        category = row.get("category", None)
        level = LogLevel.parse_type(row.get("level", "INFO"))
        message = row.get("message", "__UNDEFINED__")
        return make_log_record_output(category, level, message,
                                      format, datefmt, **kwargs)

    @staticmethod
    def annotate_with_row_schema(table, row_schema):
        """
        Annotate/extend a table of log-records with additional columns from
        the log-record schema if columns are missing.

        :param table:   Table w/ log-records (as :class:`behave.model.Table`)
        :param row_schema:  Log-record row schema (as dict).
        """
        for column, value in row_schema.items():
            if column not in table.headings:
                table.add_column(column, default_value=value)


# -----------------------------------------------------------------------------
# STEP DEFINITIONS:
# -----------------------------------------------------------------------------
# @step('I create log records for the following categories')
# def step_I_create_logrecords_for_categories_with_text(context):
#     assert context.text is not None, "REQUIRE: context.text"
#     current_level = context.config.logging_level
#     categories = context.text.split()
#     for category_name in categories:
#         logger = logging.getLogger(category_name)
#         logger.log(current_level, "__LOG_RECORD__")

@step('I create log records with')
def step_I_create_logrecords_with_table(context):
    """
    Step definition that creates one more log records by using a table.

    .. code-block: gherkin

        When I create log records with:
            | category | level | message   |
            |  foo     | ERROR | Hello Foo |
            |  foo.bar | WARN  | Hello Foo.Bar |

    Table description
    ------------------

    | Column   | Type     | Required | Description |
    | category | string   | yes      | Category (or logger) to use. |
    | level    | LogLevel | yes      | Log level to use.   |
    | message  | string   | yes      | Log message to use. |

    .. code-block: python

        import logging
        from behave.configuration import LogLevel
        for row in table.rows:
            logger = logging.getLogger(row.category)
            level  = LogLevel.parse_type(row.level)
            logger.log(level, row.message)
    """
    assert context.table, "REQUIRE: context.table"
    context.table.require_columns(["category", "level", "message"])
    for row in context.table.rows:
        category = row["category"]
        if category == "__ROOT__":
            category = None
        level = LogLevel.parse_type(row["level"])
        message = row["message"]
        make_log_record(category, level, message)


@step('I create a log record with')
def step_I_create_logrecord_with_table(context):
    """
    Create an log record by using a table to provide the parts.

    .. seealso: :func:`step_I_create_logrecords_with_table()`
    """
    assert context.table, "REQUIRE: context.table"
    assert len(context.table.rows) == 1, "REQUIRE: table.row.size == 1"
    step_I_create_logrecords_with_table(context)

@step('I define the log record schema')
def step_I_define_logrecord_schema_with_table(context):
    assert context.table, "REQUIRE: context.table"
    context.table.require_columns(["category", "level", "message"])
    assert len(context.table.rows) == 1, \
        "REQUIRE: context.table.rows.size(%s) == 1" % (len(context.table.rows))

    row = context.table.rows[0]
    row_schema = dict(category=row["category"], level=row["level"],
                  message=row["message"])
    context.log_record_row_schema = row_schema


@then('the command output should contain the following log records')
def step_command_output_should_contain_log_records(context):
    """
    Verifies that the command output contains the specified log records
    (in any order).

    .. code-block: gherkin

        Then the command output should contain the following log records:
            | category | level   | message |
            | bar      | CURRENT | xxx     |
    """
    assert context.table, "REQUIRE: context.table"
    context.table.require_columns(["category", "level", "message"])
    format = getattr(context, "log_record_format", context.config.logging_format)
    for row in context.table.rows:
        output = LogRecordTable.make_output_for_row(row, format)
        context.execute_steps(u'''
            Then the command output should contain:
                """
                {expected_output}
                """
            '''.format(expected_output=output))


@then('the command output should not contain the following log records')
def step_command_output_should_not_contain_log_records(context):
    """
    Verifies that the command output contains the specified log records
    (in any order).

    .. code-block: gherkin

        Then the command output should contain the following log records:
            | category | level   | message |
            | bar      | CURRENT | xxx     |
    """
    assert context.table, "REQUIRE: context.table"
    context.table.require_columns(["category", "level", "message"])
    format = getattr(context, "log_record_format", context.config.logging_format)
    for row in context.table.rows:
        output = LogRecordTable.make_output_for_row(row, format)
        context.execute_steps(u'''
            Then the command output should not contain:
                """
                {expected_output}
                """
            '''.format(expected_output=output))

@then('the command output should contain the following log record')
def step_command_output_should_contain_log_record(context):
    assert context.table, "REQUIRE: context.table"
    assert len(context.table.rows) == 1, "REQUIRE: table.row.size == 1"
    step_command_output_should_contain_log_records(context)


@then('the command output should not contain the following log record')
def step_command_output_should_not_contain_log_record(context):
    assert context.table, "REQUIRE: context.table"
    assert len(context.table.rows) == 1, "REQUIRE: table.row.size == 1"
    step_command_output_should_not_contain_log_records(context)

@then('the command output should contain log records from categories')
def step_command_output_should_contain_log_records_from_categories(context):
    """
    Verifies that the command output contains the specified log records
    (in any order).

    .. code-block: gherkin

        Given I define a log record schema:
            | category | level | message |
            | root     | ERROR | __LOG_MESSAGE__ |
        Then the command output should contain log records from categories:
            | category |
            | bar      |
    """
    assert context.table, "REQUIRE: context.table"
    context.table.require_column("category")
    record_schema = context.log_record_row_schema
    LogRecordTable.annotate_with_row_schema(context.table, record_schema)
    step_command_output_should_contain_log_records(context)
    context.table.remove_columns(["level", "message"])


@then('the command output should not contain log records from categories')
def step_command_output_should_not_contain_log_records_from_categories(context):
    """
    Verifies that the command output contains not log records from
    the provided log categories (in any order).

    .. code-block: gherkin

        Given I define the log record schema:
            | category | level | message |
            | root     | ERROR | __LOG_MESSAGE__ |
        Then the command output should not contain log records from categories:
            | category |
            | bar      |
    """
    assert context.table, "REQUIRE: context.table"
    context.table.require_column("category")
    record_schema = context.log_record_row_schema
    LogRecordTable.annotate_with_row_schema(context.table, record_schema)
    step_command_output_should_not_contain_log_records(context)
    context.table.remove_columns(["level", "message"])

@then('the file "{filename}" should contain the log records')
def step_file_should_contain_log_records(context, filename):
    """
    Verifies that the command output contains the specified log records
    (in any order).

    .. code-block: gherkin

        Then the file "xxx.log" should contain the log records:
            | category | level   | message |
            | bar      | CURRENT | xxx     |
    """
    assert context.table, "REQUIRE: context.table"
    context.table.require_columns(["category", "level", "message"])
    format = getattr(context, "log_record_format", context.config.logging_format)
    for row in context.table.rows:
        output = LogRecordTable.make_output_for_row(row, format)
        context.text = output
        step_file_should_contain_multiline_text(context, filename)

@then('the file "{filename}" should not contain the log records')
def step_file_should_not_contain_log_records(context, filename):
    """
    Verifies that the command output contains the specified log records
    (in any order).

    .. code-block: gherkin

        Then the file "xxx.log" should not contain the log records:
            | category | level   | message |
            | bar      | CURRENT | xxx     |
    """
    assert context.table, "REQUIRE: context.table"
    context.table.require_columns(["category", "level", "message"])
    format = getattr(context, "log_record_format", context.config.logging_format)
    for row in context.table.rows:
        output = LogRecordTable.make_output_for_row(row, format)
        context.text = output
        step_file_should_not_contain_multiline_text(context, filename)


@step('I use "{log_record_format}" as log record format')
def step_use_log_record_format_text(context, log_record_format):
    context.log_record_format = log_record_format

@step('I use the log record configuration')
def step_use_log_record_configuration(context):
    """
    Define log record configuration parameters.

    .. code-block: gherkin

        Given I use the log record configuration:
            | property | value |
            | format   |       |
            | datefmt  |       |
    """
    assert context.table, "REQUIRE: context.table"
    context.table.require_columns(["property", "value"])
    for row in context.table.rows:
        property_name = row["property"]
        value = row["value"]
        if property_name == "format":
            context.log_record_format = value
        elif property_name == "datefmt":
            context.log_record_datefmt = value
        else:
            raise KeyError("Unknown property=%s" % property_name)


# -----------------------------------------------------------------------------
# TODO: STEP DEFINITIONS:
# -----------------------------------------------------------------------------
@step('I capture log records with level "{level}" or above')
def step_I_capture_logrecords(context, level):
    raise NotImplementedError()


@step('I capture log records')
def step_I_capture_logrecords(context):
    """

    .. code-block: gherkin
        Given I capture log records
        When I capture log records

    :param context:
    """
    raise NotImplementedError()
    logcapture = getattr(context, "logcapture", None)
    if not logcapture:
        context.logcapture = LoggingCapture()
