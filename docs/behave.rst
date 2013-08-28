==============
*behave* usage
==============

The command-line tool *behave* has a bunch of `command-line arguments`_ and is
also configurable using `configuration files`_.

Values defined in the configuration files are used as defaults which the
command-line arguments may override.


Command-Line Arguments
======================

You may see the same information presented below at any time using ``behave
-h``.

**-c, --no-color**
   Disable the use of ANSI color escapes.
**--color**
   Use ANSI color escapes. This is the default behaviour. This switch
   is used to override a configuration file setting.
**-d, --dry-run**
   Invokes formatters without executing the steps.
**-e, --exclude**
   Don't run feature files matching regular expression PATTERN.
**-i, --include**
   Only run feature files matching regular expression PATTERN.
**--no-junit**
   Don't output JUnit-compatible reports.
**--junit**
   Output JUnit-compatible reports. When junit is enabled, all stdout
   and stderr will be redirected and dumped to the junit report,
   regardless of the '--capture' and '--no-capture' options.
**--junit-directory**
   Directory in which to store JUnit reports.
**-f, --format**
   Specify a formatter. If none is specified the default formatter is
   used. Pass '--format help' to get a list of available formatters.
**-k, --no-skipped**
   Don't print skipped steps (due to tags).
**--show-skipped**
   Print skipped steps. This is the default behaviour. This switch is
   used to override a configuration file setting.
**--no-snippets**
   Don't print snippets for unimplemented steps.
**--snippets**
   Print snippets for unimplemented steps. This is the default
   behaviour. This switch is used to override a configuration file
   setting.
**-m, --no-multiline**
   Don't print multiline strings and tables under steps.
**--multiline**
   Print multiline strings and tables under steps. This is the default
   behaviour. This switch is used to override a configuration file
   setting.
**-n, --name**
   Only execute the feature elements which match part of the given
   name. If this option is given more than once, it will match against
   all the given names.
**--no-capture**
   Don't capture stdout (any stdout output will be printed
   immediately.)
**--capture**
   Capture stdout (any stdout output will be printed if there is a
   failure.) This is the default behaviour. This switch is used to
   override a configuration file setting.
**--no-capture-stderr**
   Don't capture stderr (any stderr output will be printed
   immediately.)
**--capture-stderr**
   Capture stderr (any stderr output will be printed if there is a
   failure.) This is the default behaviour. This switch is used to
   override a configuration file setting.
**--no-logcapture**
   Don't capture logging. Logging configuration will be left intact.
**--logcapture**
   Capture logging. All logging during a step will be captured and
   displayed in the event of a failure. This is the default behaviour.
   This switch is used to override a configuration file setting.
**--logging-format**
   Specify custom format to print statements. Uses the same format as
   used by standard logging handlers. The default is
   '%(levelname)s:%(name)s:%(message)s'.
**--logging-level**
   Specify a level to capture logging at. The default is NOTSET -
   capturing everything.
**--logging-datefmt**
   Specify custom date/time format to print statements. Uses the same
   format as used by standard logging handlers.
**--logging-filter**
   Specify which statements to filter in/out. By default, everything
   is captured. If the output is too verbose, use this option to
   filter out needless output. Example: --logging-filter=foo will
   capture statements issued ONLY to foo or foo.what.ever.sub but not
   foobar or other logger. Specify multiple loggers with comma:
   filter=foo,bar,baz. If any logger name is prefixed with a minus, eg
   filter=-foo, it will be excluded rather than included.
**--logging-clear-handlers**
   Clear all other logging handlers.
**--no-summary**
   Don't display the summary at the end of the run.
**--summary**
   Display the summary at the end of the run.
**-o, --outfile**
   Write to specified file instead of stdout.
**-q, --quiet**
   Alias for --no-snippets --no-source.
**-s, --no-source**
   Don't print the file and line of the step definition with the
   steps.
**--show-source**
   Print the file and line of the step definition with the steps. This
   is the default behaviour. This switch is used to override a
   configuration file setting.
**--stop**
   Stop running tests at the first failure.
**-t, --tags**
   Only execute features or scenarios with tags matching
   TAG_EXPRESSION. Pass '--tags-help' for more information.
**-T, --no-timings**
   Don't print the time taken for each step.
**--show-timings**
   Print the time taken, in seconds, of each step after the step has
   completed. This is the default behaviour. This switch is used to
   override a configuration file setting.
**-v, --verbose**
   Show the files and features loaded.
**-w, --wip**
   Only run scenarios tagged with "wip". Additionally: use the "plain"
   formatter, do not capture stdout or logging output and stop at the
   first failure.
**-x, --expand**
   Expand scenario outline tables in output.
**--lang**
   Use keywords for a language other than English.
**--lang-list**
   List the languages available for --lang.
**--lang-help**
   List the translations accepted for one language.
**--tags-help**
   Show help for tag expressions.
**--version**
   Show version.


Tag Expression
--------------

Scenarios inherit tags declared on the Feature level. The simplest
TAG_EXPRESSION is simply a tag::

    --tags @dev

You may even leave off the "@" - behave doesn't mind.

When a tag in a tag expression starts with a ~, this represents boolean NOT::

    --tags ~@dev

A tag expression can have several tags separated by a comma, which represents
logical OR::

    --tags @dev,@wip

The --tags option can be specified several times, and this represents logical
AND, for instance this represents the boolean expression
"(@foo or not @bar) and @zap"::

    --tags @foo,~@bar --tags @zap.

Beware that if you want to use several negative tags to exclude several tags
you have to use logical AND::

    --tags ~@fixme --tags ~@buggy.


Configuration Files
===================

Configuration files for *behave* are called either ".behaverc" or
"behave.ini" (your preference) and are located in one of three places:

1. the current working directory (good for per-project settings),
2. your home directory ($HOME), or
3. on Windows, in the %APPDATA% directory.

If you are wondering where *behave* is getting its configuration defaults
from you can use the "-v" command-line argument and it'll tell you.

Confuguration files **must** start with the label "[behave]" and are
formatted in the Windows INI style, for example:

.. code-block:: ini
  
  [behave]
  format=plain
  logging_clear_handlers=yes
  logging_filter=-suds

The types possible are:

**text**
  This just assigns whatever text you supply to the configuration setting.

**boolean**
  This assigns a boolean value to the configuration setting. True values
  are "1", "yes", "true", and "on". False values are "0", "no", "false",
  and "off".

**text (multiple allowed)**
  These fields accept one or more values on new lines, for example a tag
  expression might look like:

  .. code-block:: ini

    tags=@foo,~@bar
         @zap

  which is the equivalent of the command-line usage::

    --tags @foo,~@bar --tags @zap.


Recognised Settings
-------------------

**color** -- boolean
   Disable the use of ANSI color escapes.
**color** -- boolean
   Use ANSI color escapes. This is the default behaviour. This switch
   is used to override a configuration file setting.
**dry_run** -- boolean
   Invokes formatters without executing the steps.
**exclude_re** -- text
   Don't run feature files matching regular expression PATTERN.
**include_re** -- text
   Only run feature files matching regular expression PATTERN.
**junit** -- boolean
   Don't output JUnit-compatible reports.
**junit** -- boolean
   Output JUnit-compatible reports. When junit is enabled, all stdout
   and stderr will be redirected and dumped to the junit report,
   regardless of the '--capture' and '--no-capture' options.
**junit_directory** -- text
   Directory in which to store JUnit reports.
**default_format** -- text
   Specify default formatter (default: pretty).
**format** -- text (multiple allowed)
   Specify a formatter. If none is specified the default formatter is
   used. Pass '--format help' to get a list of available formatters.
**show_skipped** -- boolean
   Don't print skipped steps (due to tags).
**show_skipped** -- boolean
   Print skipped steps. This is the default behaviour. This switch is
   used to override a configuration file setting.
**show_snippets** -- boolean
   Don't print snippets for unimplemented steps.
**show_snippets** -- boolean
   Print snippets for unimplemented steps. This is the default
   behaviour. This switch is used to override a configuration file
   setting.
**show_multiline** -- boolean
   Don't print multiline strings and tables under steps.
**show_multiline** -- boolean
   Print multiline strings and tables under steps. This is the default
   behaviour. This switch is used to override a configuration file
   setting.
**name** -- text (multiple allowed)
   Only execute the feature elements which match part of the given
   name. If this option is given more than once, it will match against
   all the given names.
**stdout_capture** -- boolean
   Don't capture stdout (any stdout output will be printed
   immediately.)
**stdout_capture** -- boolean
   Capture stdout (any stdout output will be printed if there is a
   failure.) This is the default behaviour. This switch is used to
   override a configuration file setting.
**stderr_capture** -- boolean
   Don't capture stderr (any stderr output will be printed
   immediately.)
**stderr_capture** -- boolean
   Capture stderr (any stderr output will be printed if there is a
   failure.) This is the default behaviour. This switch is used to
   override a configuration file setting.
**log_capture** -- boolean
   Don't capture logging. Logging configuration will be left intact.
**log_capture** -- boolean
   Capture logging. All logging during a step will be captured and
   displayed in the event of a failure. This is the default behaviour.
   This switch is used to override a configuration file setting.
**logging_format** -- text
   Specify custom format to print statements. Uses the same format as
   used by standard logging handlers. The default is
   '%(levelname)s:%(name)s:%(message)s'.
**logging_level** -- text
   Specify a level to capture logging at. The default is NOTSET -
   capturing everything.
**logging_datefmt** -- text
   Specify custom date/time format to print statements. Uses the same
   format as used by standard logging handlers.
**logging_filter** -- text
   Specify which statements to filter in/out. By default, everything
   is captured. If the output is too verbose, use this option to
   filter out needless output. Example: ``logging_filter = foo`` will
   capture statements issued ONLY to "foo" or "foo.what.ever.sub" but
   not "foobar" or other logger. Specify multiple loggers with comma:
   ``logging_filter = foo,bar,baz``. If any logger name is prefixed
   with a minus, eg ``logging_filter = -foo``, it will be excluded
   rather than included.
**logging_clear_handlers** -- boolean
   Clear all other logging handlers.
**summary** -- boolean
   Don't display the summary at the end of the run.
**summary** -- boolean
   Display the summary at the end of the run.
**outfiles** -- text (multiple allowed)
   Write to specified file instead of stdout.
**paths** -- text (multiple allowed)
   Specify default feature paths, used when none are provided.
**quiet** -- boolean
   Alias for --no-snippets --no-source.
**show_source** -- boolean
   Don't print the file and line of the step definition with the
   steps.
**show_source** -- boolean
   Print the file and line of the step definition with the steps. This
   is the default behaviour. This switch is used to override a
   configuration file setting.
**stop** -- boolean
   Stop running tests at the first failure.
**tags** -- text (multiple allowed)
   Only execute certain features or scenarios based on the tag
   expression given. See below for how to code tag expressions in
   configuration files.
**show_timings** -- boolean
   Don't print the time taken for each step.
**show_timings** -- boolean
   Print the time taken, in seconds, of each step after the step has
   completed. This is the default behaviour. This switch is used to
   override a configuration file setting.
**verbose** -- boolean
   Show the files and features loaded.
**wip** -- boolean
   Only run scenarios tagged with "wip". Additionally: use the "plain"
   formatter, do not capture stdout or logging output and stop at the
   first failure.
**expand** -- boolean
   Expand scenario outline tables in output.
**lang** -- text
   Use keywords for a language other than English.


