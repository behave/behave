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

.. option:: --color

    Use colored mode or not (default: auto).

.. option:: -d, --dry-run

    Invokes formatters without executing the steps.

.. option:: -D, --define

    Define user-specific data for the config.userdata dictionary. Example:
    -D foo=bar to store it in config.userdata["foo"].

.. option:: -e, --exclude

    Don't run feature files matching regular expression PATTERN.

.. option:: -i, --include

    Only run feature files matching regular expression PATTERN.

.. option:: --no-junit

    Don't output JUnit-compatible reports.

.. option:: --junit

    Output JUnit-compatible reports. When junit is enabled, all stdout and
    stderr will be redirected and dumped to the junit report,
    regardless of the "--capture" and "--no-capture" options.

.. option:: --junit-directory

    Directory in which to store JUnit reports.

.. option:: -j, --jobs, --parallel

    Number of concurrent jobs to use (default: 1). Only supported by test
    runners that support parallel execution.

.. option:: -f, --format

    Specify a formatter. If none is specified the default formatter is
    used. Pass "--format help" to get a list of available formatters.

.. option:: --steps-catalog

    Show a catalog of all available step definitions. SAME AS:
    --format=steps.catalog --dry-run --no-summary -q

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

.. option:: -n, --name

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

.. option:: --logging-level

    Specify a level to capture logging at. The default is INFO - capturing
    everything.

.. option:: --logging-format

    Specify custom format to print statements. Uses the same format as
    used by standard logging handlers. The default is
    "%(levelname)s:%(name)s:%(message)s".

.. option:: --logging-datefmt

    Specify custom date/time format to print statements. Uses the same
    format as used by standard logging handlers.

.. option:: --logging-filter

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

.. option:: -o, --outfile

    Write to specified file instead of stdout.

.. option:: -q, --quiet

    Alias for --no-snippets --no-source.

.. option:: -r, --runner

    Use own runner class, like: "behave.runner:Runner"

.. option:: --no-source

    Don't print the file and line of the step definition with the steps.

.. option:: --show-source

    Print the file and line of the step definition with the steps. This is
    the default behaviour. This switch is used to override a
    configuration file setting.

.. option:: --stage

    Defines the current test stage. The test stage name is used as name
    prefix for the environment file and the steps directory (instead
    of default path names).

.. option:: --stop

    Stop running tests at the first failure.

.. option:: -t, --tags

    Only execute features or scenarios with tags matching TAG_EXPRESSION.
    Pass "--tags-help" for more information.

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

.. option:: --lang

    Use keywords for a language other than English.

.. option:: --lang-list

    List the languages available for --lang.

.. option:: --lang-help

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

NOTES:

* The tag-prefix "@" is optional.
* An empty tag-expression is "true" (select-anything).

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
    format=plain
    logging_clear_handlers=yes
    logging_filter=-suds

Alternatively, if using "pyproject.toml" instead (note the "tool." prefix):

.. code-block:: toml

    [tool.behave]
    format = "plain"
    logging_clear_handlers = true
    logging_filter = "-suds"

NOTE: toml does not support `'%'` interpolations.

Configuration Parameter Types
-----------------------------

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


Configuration Parameters
-----------------------------

.. index::
    single: configuration param; color

.. describe:: color : Colored (Enum)

    Use colored mode or not (default: auto).

.. index::
    single: configuration param; dry_run

.. describe:: dry_run : bool

    Invokes formatters without executing the steps.

.. index::
    single: configuration param; userdata_defines

.. describe:: userdata_defines : sequence<text>

    Define user-specific data for the config.userdata dictionary. Example:
    -D foo=bar to store it in config.userdata["foo"].

.. index::
    single: configuration param; exclude_re

.. describe:: exclude_re : text

    Don't run feature files matching regular expression PATTERN.

.. index::
    single: configuration param; include_re

.. describe:: include_re : text

    Only run feature files matching regular expression PATTERN.

.. index::
    single: configuration param; junit

.. describe:: junit : bool

    Output JUnit-compatible reports. When junit is enabled, all stdout and
    stderr will be redirected and dumped to the junit report,
    regardless of the "--capture" and "--no-capture" options.

.. index::
    single: configuration param; junit_directory

.. describe:: junit_directory : text

    Directory in which to store JUnit reports.

.. index::
    single: configuration param; jobs

.. describe:: jobs : positive_number

    Number of concurrent jobs to use (default: 1). Only supported by test
    runners that support parallel execution.

.. index::
    single: configuration param; default_format

.. describe:: default_format : text

    Specify default formatter (default: pretty).

.. index::
    single: configuration param; format

.. describe:: format : sequence<text>

    Specify a formatter. If none is specified the default formatter is
    used. Pass "--format help" to get a list of available formatters.

.. index::
    single: configuration param; steps_catalog

.. describe:: steps_catalog : bool

    Show a catalog of all available step definitions. SAME AS:
    --format=steps.catalog --dry-run --no-summary -q

.. index::
    single: configuration param; scenario_outline_annotation_schema

.. describe:: scenario_outline_annotation_schema : text

    Specify name annotation schema for scenario outline (default="{name}
    -- @{row.id} {examples.name}").

.. index::
    single: configuration param; show_skipped

.. describe:: show_skipped : bool

    Print skipped steps. This is the default behaviour. This switch is
    used to override a configuration file setting.

.. index::
    single: configuration param; show_snippets

.. describe:: show_snippets : bool

    Print snippets for unimplemented steps. This is the default behaviour.
    This switch is used to override a configuration file setting.

.. index::
    single: configuration param; show_multiline

.. describe:: show_multiline : bool

    Print multiline strings and tables under steps. This is the default
    behaviour. This switch is used to override a configuration file
    setting.

.. index::
    single: configuration param; name

.. describe:: name : sequence<text>

    Select feature elements (scenarios, ...) to run which match part of
    the given name (regex pattern). If this option is given more than
    once, it will match against all the given names.

.. index::
    single: configuration param; capture

.. describe:: capture : bool

    Enable capture mode (stdout/stderr/log-output). Any capture output
    will be printed on a failure/error.

.. index::
    single: configuration param; capture_stdout

.. describe:: capture_stdout : bool

    Enable capture of stdout.

.. index::
    single: configuration param; capture_stderr

.. describe:: capture_stderr : bool

    Enable capture of stderr.

.. index::
    single: configuration param; capture_log

.. describe:: capture_log : bool

    Enable capture of logging output.

.. index::
    single: configuration param; capture_hooks

.. describe:: capture_hooks : bool

    Enable capture of hooks (except: before_all).

.. index::
    single: configuration param; logging_level

.. describe:: logging_level : text

    Specify a level to capture logging at. The default is INFO - capturing
    everything.

.. index::
    single: configuration param; logging_format

.. describe:: logging_format : text

    Specify custom format to print statements. Uses the same format as
    used by standard logging handlers. The default is
    "%(levelname)s:%(name)s:%(message)s".

.. index::
    single: configuration param; logging_datefmt

.. describe:: logging_datefmt : text

    Specify custom date/time format to print statements. Uses the same
    format as used by standard logging handlers.

.. index::
    single: configuration param; logging_filter

.. describe:: logging_filter : text

    Specify which statements to filter in/out. By default, everything is
    captured. If the output is too verbose, use this option to filter
    out needless output. Example: ``logging_filter = foo`` will
    capture statements issued ONLY to "foo" or "foo.what.ever.sub" but
    not "foobar" or other logger. Specify multiple loggers with comma:
    ``logging_filter = foo,bar,baz``. If any logger name is prefixed
    with a minus, eg ``logging_filter = -foo``, it will be excluded
    rather than included.

.. index::
    single: configuration param; logging_clear_handlers

.. describe:: logging_clear_handlers : bool

    Clear existing logging handlers (during capture-log).

.. index::
    single: configuration param; summary

.. describe:: summary : bool

    Display the summary at the end of the run.

.. index::
    single: configuration param; outfiles

.. describe:: outfiles : sequence<text>

    Write to specified file instead of stdout.

.. index::
    single: configuration param; paths

.. describe:: paths : sequence<text>

    Specify default feature paths, used when none are provided.

.. index::
    single: configuration param; tag_expression_protocol

.. describe:: tag_expression_protocol : TagExpressionProtocol (Enum)

    Specify the tag-expression protocol to use (default: auto_detect).
    With "v1", only tag-expressions v1 are supported. With "v2", only
    tag-expressions v2 are supported. With "auto_detect", tag-
    expressions v1 and v2 are auto-detected.

.. index::
    single: configuration param; quiet

.. describe:: quiet : bool

    Alias for --no-snippets --no-source.

.. index::
    single: configuration param; runner

.. describe:: runner : text

    Use own runner class, like: "behave.runner:Runner"

.. index::
    single: configuration param; show_source

.. describe:: show_source : bool

    Print the file and line of the step definition with the steps. This is
    the default behaviour. This switch is used to override a
    configuration file setting.

.. index::
    single: configuration param; stage

.. describe:: stage : text

    Defines the current test stage. The test stage name is used as name
    prefix for the environment file and the steps directory (instead
    of default path names).

.. index::
    single: configuration param; stop

.. describe:: stop : bool

    Stop running tests at the first failure.

.. index::
    single: configuration param; default_tags

.. describe:: default_tags : sequence<text>

    Define default tags when non are provided. See --tags for more
    information.

.. index::
    single: configuration param; tags

.. describe:: tags : sequence<text>

    Only execute certain features or scenarios based on the tag expression
    given. See below for how to code tag expressions in configuration
    files.

.. index::
    single: configuration param; show_timings

.. describe:: show_timings : bool

    Print the time taken, in seconds, of each step after the step has
    completed. This is the default behaviour. This switch is used to
    override a configuration file setting.

.. index::
    single: configuration param; verbose

.. describe:: verbose : bool

    Show the files and features loaded.

.. index::
    single: configuration param; wip

.. describe:: wip : bool

    Only run scenarios tagged with "wip". Additionally: use the "plain"
    formatter, do not capture stdout or logging output and stop at the
    first failure.

.. index::
    single: configuration param; lang

.. describe:: lang : text

    Use keywords for a language other than English.



