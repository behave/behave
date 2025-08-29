.. _id.using_behave:

==============
Using *behave*
==============

The command-line tool *behave* has a bunch of `command-line arguments`_ and is
also configurable using `configuration files`_.

Values defined in the configuration files are used as defaults which the
command-line arguments may override.


Command-Line Arguments
======================

You may see the same information presented below at any time using ``behave
-h``.

.. option:: -C, --no-color

    Disable colored mode.

.. option:: --color COLORED

    Use colored mode or not (default: auto).

.. option:: -d, --dry-run

    Invokes formatters without executing the steps.

.. option:: -D NAME=VALUE, --define NAME=VALUE

    Define user-specific data for the config.userdata dictionary. Example:
    -D foo=bar to store it in config.userdata["foo"].

.. option:: -e PATTERN, --exclude PATTERN

    Don't run feature files matching regular expression PATTERN.

.. option:: -i PATTERN, --include PATTERN

    Only run feature files matching regular expression PATTERN.

.. option:: --no-junit

    Don't output JUnit-compatible reports.

.. option:: --junit

    Output JUnit-compatible reports. When junit is enabled, all stdout and
    stderr will be redirected and dumped to the junit report,
    regardless of the "--capture" and "--no-capture" options.

.. option:: --junit-directory PATH

    Directory in which to store JUnit reports.

.. option:: -j NUMBER, --jobs NUMBER, --parallel NUMBER

    Number of concurrent jobs to use (default: 1). Only supported by test
    runners that support parallel execution.

.. option:: -f FORMATTER, --format FORMATTER

    Specify a formatter. If none is specified the default formatter is
    used. Pass "--format help" to get a list of available formatters.

.. option:: --steps-catalog

    Show a catalog of all available step definitions. SAME AS: "--
    format=steps.catalog --dry-run --no-summary -q".

.. option:: --no-skipped

    Don't print skipped steps (due to tags).

.. option:: --show-skipped

    Print skipped steps. This is the default behaviour. This switch is
    used to override a configuration file setting.

.. option:: --no-snippets

    Don't print snippets for unimplemented steps.

.. option:: --snippets

    Print snippets for unimplemented steps. This is the default behaviour.
    This switch is used to override a configuration file setting.

.. option:: --no-multiline

    Don't print multiline strings and tables under steps.

.. option:: --multiline

    Print multiline strings and tables under steps. This is the default
    behaviour. This switch is used to override a configuration file
    setting.

.. option:: -n NAME_PATTERN, --name NAME_PATTERN

    Select feature elements (scenarios, ...) to run which match part of
    the given name (regex pattern). If this option is given more than
    once, it will match against all the given names.

.. option:: --capture

    Enable capture mode (stdout/stderr/log-output). Any capture output
    will be printed on a failure/error.

.. option:: --no-capture

    Disable capture mode (stdout/stderr/log-output).

.. option:: --capture-stdout

    Enable capture of stdout.

.. option:: --no-capture-stdout

    Disable capture of stdout.

.. option:: --capture-stderr

    Enable capture of stderr.

.. option:: --no-capture-stderr

    Disable capture of stderr.

.. option:: --capture-log, --logcapture

    Enable capture of logging output.

.. option:: --no-capture-log, --no-logcapture

    Disable capture of logging output.

.. option:: --capture-hooks

    Enable capture of hooks (except: before_all).

.. option:: --no-capture-hooks

    Disable capture of hooks.

.. option:: --logging-level LOG_LEVEL

    Specify a level to capture logging at. The default is INFO - capturing
    everything.

.. option:: --logging-format LOG_FORMAT

    Specify custom format to print statements. Uses the same format as
    used by standard logging handlers. The default is
    "%(levelname)s:%(name)s:%(message)s".

.. option:: --logging-datefmt LOG_DATE_FORMAT

    Specify custom date/time format to print statements. Uses the same
    format as used by standard logging handlers.

.. option:: --logging-filter LOG_FILTER

    Specify which statements to filter in/out. By default, everything is
    captured. If the output is too verbose, use this option to filter
    out needless output. Example: --logging-filter=foo will capture
    statements issued ONLY to foo or foo.what.ever.sub but not foobar
    or other logger. Specify multiple loggers with comma:
    filter=foo,bar,baz. If any logger name is prefixed with a minus,
    eg filter=-foo, it will be excluded rather than included.

.. option:: --logging-clear-handlers

    Clear existing logging handlers (during capture-log).

.. option:: --no-logging-clear-handlers

    Keep existing logging handlers (during capture-log).

.. option:: --no-summary

    Don't display the summary at the end of the run.

.. option:: --summary

    Display the summary at the end of the run.

.. option:: -o FILENAME, --outfile FILENAME

    Write formatter output to output-file (default: stdout).

.. option:: -q, --quiet

    Alias for --no-snippets --no-source.

.. option:: -r RUNNER_CLASS, --runner RUNNER_CLASS

    Use own runner class, like: "behave.runner:Runner"

.. option:: --no-source

    Don't print the file and line of the step definition with the steps.

.. option:: --show-source

    Print the file and line of the step definition with the steps. This is
    the default behaviour. This switch is used to override a
    configuration file setting.

.. option:: --stage TEXT

    Defines the current test stage. The test stage name is used as name
    prefix for the environment file and the steps directory (instead
    of default path names).

.. option:: --stop

    Stop running tests at the first failure.

.. option:: -t TAG_EXPRESSION, --tags TAG_EXPRESSION

    Only execute features or scenarios with tags matching TAG_EXPRESSION.
    Use :option:`--tags-help` option for more information.

.. option:: -T, --no-timings

    Don't print the time taken for each step.

.. option:: --show-timings

    Print the time taken, in seconds, of each step after the step has
    completed. This is the default behaviour. This switch is used to
    override a configuration file setting.

.. option:: -v, --verbose

    Show the files and features loaded.

.. option:: -w, --wip

    Only run scenarios tagged with "wip". Additionally: use the "plain"
    formatter, do not capture stdout or logging output and stop at the
    first failure.

.. option:: --lang LANG

    Use keywords for a language other than English.

.. option:: --lang-list

    List the languages available for --lang.

.. option:: --lang-help LANG

    List the translations accepted for one language.

.. option:: --tags-help

    Show help for tag expressions.

.. option:: --version

    Show version.



Tag Expression
--------------

TAG-EXPRESSIONS selects Features/Rules/Scenarios by using their tags.
A TAG-EXPRESSION is a boolean expression that references some tags.

EXAMPLES:

    --tags=@smoke
    --tags="not @xfail"
    --tags="@smoke or @wip"
    --tags="@smoke and @wip"
    --tags="(@slow and not @fixme) or @smoke"
    --tags="not (@fixme or @xfail)"
    --tags="@smoke and {config.tags}"

NOTES:

* The tag-prefix "@" is optional.
* An empty tag-expression is "true" (select-anything).
* Use "{config.tags}" placeholder on command-line
  to use tag-expressions from the config-file (from: "tags" or "default_tags").

TAG-INHERITANCE:

* A Rule inherits the tags of its Feature
* A Scenario inherits the tags of its Feature or Rule.
* A Scenario of a ScenarioOutline/ScenarioTemplate inherit tags
  from this ScenarioOutline/ScenarioTemplate and its Example table.


.. _docid.behave.configuration-files:

Configuration Files
===================

Configuration files for *behave* are called either ".behaverc", "behave.ini",
"setup.cfg", "tox.ini", or "pyproject.toml" (your preference) and are located
in one of three places:

1. the current working directory (good for per-project settings),
2. your home directory ($HOME), or
3. on Windows, in the %APPDATA% directory.

If you are wondering where *behave* is getting its configuration defaults
from you can use the "-v" command-line argument and it'll tell you.

Configuration files **must** start with the label "[behave]" and are
formatted in the Windows INI style, for example:

.. code-block:: ini

    [behave]
    default_format = plain
    default_tags = not (@xfail or @not_implemented)
    junit = true
    junit_directory = build/behave.reports
    logging_level = WARNING

Alternatively, if using "pyproject.toml" instead (note the "tool." prefix):

.. code-block:: toml

    [tool.behave]
    default_format = "plain"
    default_tags = "not (@xfail or @not_implemented)"
    junit = true
    junit_directory = "build/behave.reports"
    logging_level = "WARNING"

NOTE: toml does not support `'%'` interpolations.

Configuration File Parameter Types
----------------------------------

The following types are supported (and used):

**text**
    This just assigns whatever text you supply to the configuration setting.

**bool**
    This assigns a boolean value to the configuration setting.
    The text describes the functionality when the value is true.
    True values are "1", "yes", "true", and "on".
    False values are "0", "no", "false", and "off".
    TOML: toml only accepts its native `true`

**sequence<text>**
    These fields accept one or more values on new lines, for example a tag
    expression might look like:

    .. code-block:: ini

        default_tags= (@foo or not @bar) and @zap

    which is the equivalent of the command-line usage::

        --tags="(@foo or not @bar) and @zap"

    TOML: toml can use arrays natively.


Configuration File Parameters
-----------------------------

.. index::
    single: configuration file parameter; color

.. confval:: color : Colored (Enum)

    Use colored mode or not (default: auto).

.. index::
    single: configuration file parameter; dry_run

.. confval:: dry_run : bool

    Invokes formatters without executing the steps.

.. index::
    single: configuration file parameter; exclude_re

.. confval:: exclude_re : text

    Don't run feature files matching regular expression PATTERN.

.. index::
    single: configuration file parameter; include_re

.. confval:: include_re : text

    Only run feature files matching regular expression PATTERN.

.. index::
    single: configuration file parameter; junit

.. confval:: junit : bool

    Output JUnit-compatible reports. When junit is enabled, all stdout and
    stderr will be redirected and dumped to the junit report,
    regardless of the "--capture" and "--no-capture" options.

.. index::
    single: configuration file parameter; junit_directory

.. confval:: junit_directory : text

    Directory in which to store JUnit reports.

.. index::
    single: configuration file parameter; jobs

.. confval:: jobs : positive_number

    Number of concurrent jobs to use (default: 1). Only supported by test
    runners that support parallel execution.

.. index::
    single: configuration file parameter; default_format

.. confval:: default_format : text

    Specify default formatter (default: pretty).

.. index::
    single: configuration file parameter; format

.. confval:: format : sequence<text>

    Specify a formatter. If none is specified the default formatter is
    used. Pass "--format help" to get a list of available formatters.

.. index::
    single: configuration file parameter; steps_catalog

.. confval:: steps_catalog : bool

    Show a catalog of all available step definitions. SAME AS: "--
    format=steps.catalog --dry-run --no-summary -q".

.. index::
    single: configuration file parameter; scenario_outline_annotation_schema

.. confval:: scenario_outline_annotation_schema : text

    Specify name annotation schema for scenario outline (default="{name}
    -- @{row.id} {examples.name}").

.. index::
    single: configuration file parameter; use_nested_step_modules

.. confval:: use_nested_step_modules : bool

    Use subdirectories of steps directory to import steps (default:
    false).

.. index::
    single: configuration file parameter; show_skipped

.. confval:: show_skipped : bool

    Print skipped steps. This is the default behaviour. This switch is
    used to override a configuration file setting.

.. index::
    single: configuration file parameter; show_snippets

.. confval:: show_snippets : bool

    Print snippets for unimplemented steps. This is the default behaviour.
    This switch is used to override a configuration file setting.

.. index::
    single: configuration file parameter; show_multiline

.. confval:: show_multiline : bool

    Print multiline strings and tables under steps. This is the default
    behaviour. This switch is used to override a configuration file
    setting.

.. index::
    single: configuration file parameter; name

.. confval:: name : sequence<text>

    Select feature elements (scenarios, ...) to run which match part of
    the given name (regex pattern). If this option is given more than
    once, it will match against all the given names.

.. index::
    single: configuration file parameter; capture

.. confval:: capture : bool

    Enable capture mode (stdout/stderr/log-output). Any capture output
    will be printed on a failure/error.

.. index::
    single: configuration file parameter; capture_stdout

.. confval:: capture_stdout : bool

    Enable capture of stdout.

.. index::
    single: configuration file parameter; capture_stderr

.. confval:: capture_stderr : bool

    Enable capture of stderr.

.. index::
    single: configuration file parameter; capture_log

.. confval:: capture_log : bool

    Enable capture of logging output.

.. index::
    single: configuration file parameter; capture_hooks

.. confval:: capture_hooks : bool

    Enable capture of hooks (except: before_all).

.. index::
    single: configuration file parameter; logging_level

.. confval:: logging_level : text

    Specify a level to capture logging at. The default is INFO - capturing
    everything.

.. index::
    single: configuration file parameter; logging_format

.. confval:: logging_format : text

    Specify custom format to print statements. Uses the same format as
    used by standard logging handlers. The default is
    "%(levelname)s:%(name)s:%(message)s".

.. index::
    single: configuration file parameter; logging_datefmt

.. confval:: logging_datefmt : text

    Specify custom date/time format to print statements. Uses the same
    format as used by standard logging handlers.

.. index::
    single: configuration file parameter; logging_filter

.. confval:: logging_filter : text

    Specify which statements to filter in/out. By default, everything is
    captured. If the output is too verbose, use this option to filter
    out needless output. Example: ``logging_filter = foo`` will
    capture statements issued ONLY to "foo" or "foo.what.ever.sub" but
    not "foobar" or other logger. Specify multiple loggers with comma:
    ``logging_filter = foo,bar,baz``. If any logger name is prefixed
    with a minus, eg ``logging_filter = -foo``, it will be excluded
    rather than included.

.. index::
    single: configuration file parameter; logging_clear_handlers

.. confval:: logging_clear_handlers : bool

    Clear existing logging handlers (during capture-log).

.. index::
    single: configuration file parameter; summary

.. confval:: summary : bool

    Display the summary at the end of the run.

.. index::
    single: configuration file parameter; outfiles

.. confval:: outfiles : sequence<text>

    Write formatter output to output-file (default: stdout).

.. index::
    single: configuration file parameter; paths

.. confval:: paths : sequence<text>

    Specify default feature paths, used when none are provided.

.. index::
    single: configuration file parameter; tag_expression_protocol

.. confval:: tag_expression_protocol : TagExpressionProtocol (Enum)

    Specify the tag-expression protocol to use (default: auto_detect).
    With "v1", only tag-expressions v1 are supported. With "v2", only
    tag-expressions v2 are supported. With "auto_detect", tag-
    expressions v1 and v2 are auto-detected.

.. index::
    single: configuration file parameter; quiet

.. confval:: quiet : bool

    Alias for --no-snippets --no-source.

.. index::
    single: configuration file parameter; runner

.. confval:: runner : text

    Use own runner class, like: "behave.runner:Runner"

.. index::
    single: configuration file parameter; show_source

.. confval:: show_source : bool

    Print the file and line of the step definition with the steps. This is
    the default behaviour. This switch is used to override a
    configuration file setting.

.. index::
    single: configuration file parameter; stage

.. confval:: stage : text

    Defines the current test stage. The test stage name is used as name
    prefix for the environment file and the steps directory (instead
    of default path names).

.. index::
    single: configuration file parameter; stop

.. confval:: stop : bool

    Stop running tests at the first failure.

.. index::
    single: configuration file parameter; default_tags

.. confval:: default_tags : sequence<text>

    Define default tags when non are provided. See :option:`--tags` for
    more information.

.. index::
    single: configuration file parameter; tags

.. confval:: tags : sequence<text>

    Only execute certain features or scenarios based on the tag expression
    given. See below for how to code tag expressions in configuration
    files.

.. index::
    single: configuration file parameter; show_timings

.. confval:: show_timings : bool

    Print the time taken, in seconds, of each step after the step has
    completed. This is the default behaviour. This switch is used to
    override a configuration file setting.

.. index::
    single: configuration file parameter; verbose

.. confval:: verbose : bool

    Show the files and features loaded.

.. index::
    single: configuration file parameter; wip

.. confval:: wip : bool

    Only run scenarios tagged with "wip". Additionally: use the "plain"
    formatter, do not capture stdout or logging output and stop at the
    first failure.

.. index::
    single: configuration file parameter; lang

.. confval:: lang : text

    Use keywords for a language other than English.


Additional Configuration File Sections
--------------------------------------

Section: behave.userdata
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section is used to define user-specific paramters (aka: userdata)
for the config.userdata dictionary.

.. code-block:: ini
    :caption: FILE: behave.ini

    [behave.userdata]
    foo = Alice
    bar = Bon

Alternatively, if using "pyproject.toml":

.. code-block:: toml
    :caption: FILE: pyproject.toml

    [tool.behave.userdata]
    foo = "Alice"
    bar = "Bob"

which is the equivalent of the command-line usage:

.. code-block:: shell
    :caption: SHELL

    behave -D foo=Alice -D bar=Bob ...

See :doc:`userdata` for usage examples, type conversion and advanced use cases.


Section: behave.formatters
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This configuration file section is used to:

* Define aliases for own formatters
* Override the mapping of builtin formatters

.. code-block:: ini
    :caption: FILE: behave.ini

    [behave.formatters]
    allure = allure_behave.formatter:AllureFormatter
    html   = behave_html_formatter:HTMLFormatter
    html-pretty = behave_html_pretty_formatter:PrettyHTMLFormatter

.. code-block:: toml
    :caption: FILE: pyproject.toml

    [tool.behave.formatters]
    allure = "allure_behave.formatter:AllureFormatter"
    html   = "behave_html_formatter:HTMLFormatter"
    html-pretty = "behave_html_pretty_formatter:PrettyHTMLFormatter"

You can then use this formatter alias on the command-line (or in the config-file):

.. code-block:: shell
    :caption: SHELL

    behave -f html --output=report.html ...

See :ref:`id.appendix.formatters` for more information.


Section: behave.runners
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This configuration file section is used to:

* Define aliases for own test runners
* Override the mapping of builtin test runners

.. code-block:: ini
    :caption: FILE: behave.ini

    [behave.runners]
    mine = behave4me.runner:SuperDuperRunner

.. code-block:: toml
    :caption: FILE: pyproject.toml

    [behave.runners]
    mine = "behave4me.runner:SuperDuperRunner"

You can then use this runner alias on the command-line:

.. code-block:: shell
    :caption: SHELL

    behave --runner=mine ...

See :ref:`id.appendix.runners` for more information.

