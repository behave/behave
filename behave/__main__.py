# -*- coding: utf-8 -*-
# ruff: noqa: E731

from __future__ import absolute_import, print_function
import codecs
import sys
import six
from behave.version import VERSION as BEHAVE_VERSION
from behave.configuration import Configuration
from behave.exception import (ConstraintError, ConfigError,
    FileNotFoundError, InvalidFileLocationError, InvalidFilenameError,
    ModuleNotFoundError, ClassNotFoundError, InvalidClassError,
    TagExpressionError)
from behave.importer import make_scoped_class_name
from behave.parser import ParserError
from behave.runner import Runner    # noqa: F401
from behave.runner_util import print_undefined_step_snippets, reset_runtime
from behave.runner_plugin import RunnerPlugin
from behave.textutil import compute_words_maxsize, text as _text


# ---------------------------------------------------------------------------
# CONSTANTS:
# ---------------------------------------------------------------------------
DEBUG = __debug__
TAG_EXPRESSIONS_HELP = """
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
""".strip()


# ---------------------------------------------------------------------------
# WORK-HORSE:
# ---------------------------------------------------------------------------
def run_behave(config, runner_class=None):
    """Run behave with configuration (and optional runner class).

    :param config:          Configuration object for behave.
    :param runner_class:    Runner class to use or none (use Runner class).
    :return:    0, if successful. Non-zero on failure.

    .. note:: BEST EFFORT, not intended for multi-threaded usage.
    """
    # pylint: disable=too-many-branches, too-many-statements, too-many-return-statements

    if config.version:
        print("behave " + BEHAVE_VERSION)
        return 0

    if config.tags_help:
        print_tags_help(config)
        return 0

    if  config.lang == "help" or config.lang_list:
        print_language_list()
        return 0

    if config.lang_help:
        # -- PROVIDE HELP: For one, specific language
        language = config.lang_help
        print_language_help(language)
        return 0

    if not config.format:
        config.format = [config.default_format]
    elif config.format and "format" in config.defaults:
        # -- CASE: Formatter are specified in behave configuration file.
        #    Check if formatter are provided on command-line, too.
        if len(config.format) == len(config.defaults["format"]):
            # -- NO FORMATTER on command-line: Add default formatter.
            config.format.append(config.default_format)
    if "help" in config.format:
        print_formatters()
        return 0

    if len(config.outputs) > len(config.format):
        print("CONFIG-ERROR: More outfiles (%d) than formatters (%d)." % \
              (len(config.outputs), len(config.format)))
        return 1

    if config.runner == "help":
        print_runners(config.runner_aliases)
        return 0

    # -- MAIN PART:
    runner = None
    failed = True
    try:
        reset_runtime()
        runner = RunnerPlugin(runner_class).make_runner(config)
        print("USING RUNNER: {0}".format(make_scoped_class_name(runner)))
        failed = runner.run()
    except ParserError as e:
        print(u"ParserError: %s" % e)
    except ConfigError as e:
        print(u"ConfigError: %s" % e)
    except FileNotFoundError as e:
        print(u"FileNotFoundError: %s" % e)
    except InvalidFileLocationError as e:
        print(u"InvalidFileLocationError: %s" % e)
    except InvalidFilenameError as e:
        print(u"InvalidFilenameError: %s" % e)
    except ModuleNotFoundError as e:
        print(u"ModuleNotFoundError: %s" % e)
    except ClassNotFoundError as e:
        print(u"ClassNotFoundError: %s" % e)
    except InvalidClassError as e:
        print(u"InvalidClassError: %s" % e)
    except ImportError as e:
        print(u"%s: %s" % (e.__class__.__name__, e))
        if DEBUG:
            raise
    except ConstraintError as e:
        print(u"ConstraintError: %s" % e)
    except Exception as e:
        # -- DIAGNOSTICS:
        text = _text(e)
        print(u"Exception %s: %s" % (e.__class__.__name__, text))
        raise

    if config.show_snippets and runner and runner.undefined_steps:
        print_undefined_step_snippets(runner.undefined_steps,
                                      colored=config.has_colored_mode())

    return_code = 0
    if failed:
        return_code = 1
    return return_code


# ---------------------------------------------------------------------------
# MAIN SUPPORT FOR: run_behave()
# ---------------------------------------------------------------------------
def print_tags_help(config):
    print(TAG_EXPRESSIONS_HELP)

    current_tag_expression = config.tag_expression.to_string()
    print("\nCURRENT TAG_EXPRESSION: {0}".format(current_tag_expression))
    if config.verbose:
        # -- SHOW LOW-LEVEL DETAILS:
        text = repr(config.tag_expression).replace("Literal(", "Tag(")
        print("  means: {0}".format(text))


def print_language_list(file=None):
    """Print list of supported languages, like:

    * English
    * French
    * German
    * ...
    """
    from behave.i18n import languages

    print_ = lambda text: print(text, file=file)
    if six.PY2:
        # -- PYTHON2: Overcome implicit encode problems (encoding=ASCII).
        file = codecs.getwriter("UTF-8")(file or sys.stdout)

    iso_codes = languages.keys()
    print("AVAILABLE LANGUAGES:")
    for iso_code in sorted(iso_codes):
        native = languages[iso_code]["native"]
        name = languages[iso_code]["name"]
        print_(u"  %s: %s / %s" % (iso_code, native, name))


def print_language_help(language, file=None):
    from behave.i18n import languages
    # if stream is None:
    #     stream = sys.stdout
    #     if six.PY2:
    #         # -- PYTHON2: Overcome implicit encode problems (encoding=ASCII).
    #         stream = codecs.getwriter("UTF-8")(sys.stdout)

    print_ = lambda text: print(text, file=file)
    if six.PY2:
        # -- PYTHON2: Overcome implicit encode problems (encoding=ASCII).
        file = codecs.getwriter("UTF-8")(file or sys.stdout)

    if language not in languages:
        print_("%s is not a recognised language: try --lang-list" % language)
        return 1

    trans = languages[language]
    print_(u"Translations for %s / %s" % (trans["name"], trans["native"]))
    for kw in trans:
        if kw in "name native".split():
            continue
        print_(u"%16s: %s" % (kw.title().replace("_", " "),
                             u", ".join(w for w in trans[kw] if w != "*")))


def print_formatters(file=None):
    """Prints the list of available formatters and their description.

    :param file:  Optional, output file to use (default: sys.stdout).
    """
    from behave.formatter._registry  import format_items
    from operator import itemgetter

    print_ = lambda text: print(text, file=file)

    formatter_items = sorted(format_items(resolved=True), key=itemgetter(0))
    formatter_names = [item[0]  for item in formatter_items]
    column_size = compute_words_maxsize(formatter_names)
    schema = u"  %-"+ _text(column_size) +"s  %s"
    problematic_formatters = []

    print_("AVAILABLE FORMATTERS:")
    for name, formatter_class in formatter_items:
        formatter_description = getattr(formatter_class, "description", "")
        formatter_error = getattr(formatter_class, "error", None)
        if formatter_error:
            # -- DIAGNOSTICS: Indicate if formatter definition has a problem.
            problematic_formatters.append((name, formatter_error))
        else:
            # -- NORMAL CASE:
            print_(schema % (name, formatter_description))

    if problematic_formatters:
        print_("\nUNAVAILABLE FORMATTERS:")
        for name, formatter_error in problematic_formatters:
            print_(schema % (name, formatter_error))


def print_runners(runner_aliases, file=None):
    """Print a list of known test runner classes that can be used with the
    command-line option ``--runner=RUNNER_CLASS``.

    :param runner_aliases:  List of known runner aliases (as strings)
    :param file:  Optional, to redirect print-output to a file.
    """
    # MAYBE: file = file or sys.stdout
    print_ = lambda text: print(text, file=file)

    runner_names = sorted(runner_aliases.keys())
    column_size = compute_words_maxsize(runner_names)
    schema1 = u"  %-"+ _text(column_size) +"s  = %s%s"
    schema2 = u"  %-"+ _text(column_size) +"s    %s"
    problematic_runners = []

    print_("AVAILABLE RUNNERS:")
    for runner_name in runner_names:
        scoped_class_name = runner_aliases[runner_name]
        problem = RunnerPlugin.make_problem_description(scoped_class_name, use_details=True)
        if problem:
            problematic_runners.append((runner_name, problem))
        else:
            # -- NORMAL CASE:
            print_(schema1 % (runner_name, scoped_class_name, ""))

    if problematic_runners:
        print_("\nUNAVAILABLE RUNNERS:")
        for runner_name, problem_description in problematic_runners:
            print_(schema2 % (runner_name, problem_description))


# ---------------------------------------------------------------------------
# MAIN FUNCTIONS:
# ---------------------------------------------------------------------------
def main(args=None):
    """Main function to run behave (as program).

    :param args:    Command-line args (or string) to use.
    :return: 0, if successful. Non-zero, in case of errors/failures.
    """
    try:
        config = Configuration(args)
        return run_behave(config)
    except ConfigError as e:
        exception_class_name = e.__class__.__name__
        print("%s: %s" % (exception_class_name, e))
    except TagExpressionError as e:
        print("TagExpressionError: %s" % e)
    return 1    # FAILED:

if __name__ == "__main__":
    # -- EXAMPLE: main("--version")
    sys.exit(main())
