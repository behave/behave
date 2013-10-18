Version History
===============================================================================

Version: 1.2.4a1 (unreleased)
-------------------------------------------------------------------------------

NEWS and CHANGES:

  - Running:

    * ABORT-BY-USER: Better handle KeyboardInterrupt to abort a test run.
    * feature list files (formerly: feature configfiles) support wildcards.
    * Simplify and improve setup of logging subsystem (related to: #143, #177)

  - Formatters:

    * steps.usage: Avoid duplicated steps usage due to Scenario Outlines.


IMPROVEMENT:

  * issue #108: behave.main() can be called with command-line args (provided by: medwards, jenisys)
  * issue #172: Subfolders in junit XML filenames (provided by: roignac).
  * Simple test runner to run behave tests from "setup.py"

FIXED:

  * issue #143: Logging starts with a StreamHandler way too early (provided by: jtatum, jenisys).
  * issue #175: Scenario isn't marked as 'failed' when Background step fails
  * issue #177: Cannot setup logging_format
  * issue #184: TypeError when running behave with --include option (provided by: s1ider).
  * issue #186: ScenarioOutline uses wrong return value when if fails (provided by: mdavezac)
  * issue #188: Better diagnostics if nested step is undefined
  * issue #191: Using context.execute_steps() may change context.table/.text


Version: 1.2.3 (2013-07-08)
-------------------------------------------------------------------------------

Latest stable version.
Same as last development version.


Version: 1.2.3a20 (2013-07-08)
-------------------------------------------------------------------------------

NEWS and CHANGES:

  - Install:

    * Require now parse>=1.6.2 to enforce log-bugfix #14 (was: parse>=1.6)

  - Running:

    * load_step_definitions: Are now sorted before loading (due to: Linux, ...).
    * NEW: Use lazy-loading for formatters if possible (speed up self-tests by 20%).

  - Model:

    * location: Now a FileLocation object (was: string), required for ordering.

  - Formatters:

    * NEW: progress3 formatter, ScenarioStepProgressFormatter (provided by: roignac).
    * NEW: sphinx.steps formatter, generate Sphinx-based docs for step definitions (related to #166).
    * NEW: steps formatter, shows available step definitions.
    * NEW: steps.doc formatter, shows documentation of step definitions (related to: #55).
    * NEW: steps.usage formatter, shows where step definitions are used.
    * RENAMED: json-pretty, tag_count, tag_location => json.pretty, tags, tags.location
    * help: Shows now a better formatted list (improve readability).

IMPROVEMENT:

  * issue #166: behave should have a tool (or formatter) that generates Sphinx-based documentation (basics provided).

FIXED:

  * issue #172: JUnit report filename sometimes truncated (provided by: roignac).
  * issue #171: Importing step from other step file fails with AmbiguousStep Error.
  * issue #165: FIX issue #114: do not print a blank line when the feature is skipped (provided by: florentx).
  * issue #164: StepRegistry.find_match() extends registered step_type lists.
  * issue #122: Failing selftest feature: selftest.features/duplicated_step.feature.
  * issue #110: Normalize paths provided at the command line (provided by: jesper).


Version: 1.2.3a19 (2013-05-18)
-------------------------------------------------------------------------------

NEWS and CHANGES:

  - Running (and model):

    * NEW: Support scenario file locations on command-line, ala: "{filename}:{line}" (related to: #160).
    * Formatters are now created only once (was: once for each feature).
    * Scenarios can be now be selected by name or regular expression (#87).
    * Dry-run mode: Detects now undefined steps.
    * Dry-run mode: Uses untested counts now (was using: skipped counts).
    * Run decision logic: Use ModelElement.mark_skipped() to preselect what not to run.
    * Run decision logic: Use ModelElement.should_run() to decide if element should run.

  - Parsing (and model):

    * Parser: Add support for Scenario/ScenarioOutline descriptions (related to: #79).
    * Parser: Refactor to simplify and avoid code duplications (related to: #79).
    * Parser: Improve diagnostics when parse errors occur.
    * Parser: Check that Backgrounds have no tags.
    * NEW: json_parser, parses JSON output and builds model.
    * json_parser: Add support for scenario descriptions (related to: #79).

  - Formatters:

    * INCOMPATIBLE CHANGE:
      Formatter Ctor uses now StreamOpener instead of opened Stream.
      Formatter output streams are now opened late, under control of the formatter.
      This allows the formatter to support also directory mode (if needed).
      Needed for RerunFormatter whose file was overwritten before it was read (#160).

    * NEW: RerunFormatter to simplify to rerun last failing scenarios (related to: #160).
    * NEW: TagLocationFormatter, shows where tags are used.
    * NEW: TagCountFormatter, shows which tags are used and how often (reborn).
    * JSONFormatter: Use JSON array mode now (related to: #161).
    * JSONFormatter: Added "type" to Background, Scenario, ScenerioOutline (related to: #161).
    * JSONFormatter: Added "error_message" to result (related to: #161).
    * JSONFormatter: Use now list<lines> instead of string for multi-line text (related to: #161).
    * JSONFormatter: Add support for scenario descriptions (related to: #79).
    * JSONFormatter: Generates now valid JSON (well-formed).
    * PlainFormatter: Shows now multi-line step parts (text, table), too.
    * PrettyFormatter: Enters now monochrome mode if output is piped/redirected.
    * ProgressFormatter: Flushes now output to provide better feedback.

  - Reporters:

    * JUnitReporter: Show complete scenario w/ text/tables. Improve readability.
    * SummaryReporter: Summary shows now untested items if one or more exist.

  - Testing, development:

    * tox: Use tox now in off-line mode per default (use: "tox -e init"...).
    * Add utility script to show longest step durations based on JSON data.
    * JSON: Add basic JSON schema to support JSON output validation (related to: #161).
    * JSON: Add helper script to validate JSON output against its schema (related to: #161).


IMPROVEMENT:

  * issue #161: JSONFormatter: Should use a slightly different output schema (provided by: jenisys)
  * issue #160: Support rerun file with failed features/scenarios during the last test run (provided by: jenisys)
  * issue #154: Support multiple formatters (provided by: roignac, jenisys)
  * issue #103: sort feature file by name in a given directory (provided by: gurneyalex).
  * issue #102: Add configuration file setting for specifying default feature paths (provided by: lrowe).
  * issue  #87: Add --name option support (provided by: johbo, jenisys).
  * issue  #79: Provide Support for Scenario Descriptions (provided by: caphrim007, jenisys).
  * issue  #42: Show all undefined steps taking tags into account (provided by: roignac, jenisys)

FIXED:

  * issue #162 Unnecessary ContextMaskWarnings when assert fails or exception is raised (provided by: jenisys).
  * issue #159: output stream is wrapped twice in the codecs.StreamWriter (provided by: florentx).
  * issue #153: The runtime should not by-pass the formatter to print line breaks minor.
  * issue #152: Fix encoding issues (provided by: devainandor)
  * issue #145: before_feature/after_feature should not be skipped (provided by: florentx).
  * issue #141: Don't check for full package in issue 112 (provided by: roignac).
  * issue #125: Duplicate "Captured stdout" if substep has failed (provided by: roignac).
  * issue  #60: JSONFormatter has several problems (last problem fixed).
  * issue  #48: Docs aren't clear on how Background is to be used.
  * issue  #47: Formatter processing chain is broken (solved by: #154).
  * issue  #33: behave 1.1.0: Install fails under Windows (verified, solved already some time ago).
  * issue  #28: Install fails on Windows (verified, solved already some time ago).


Version: 1.2.2.18 (2013-03-20)
-------------------------------------------------------------------------------

NEWS and CHANGES:

  * NullFormatter provided
  * model.Row: Changed Ctor parameter ordering, move seldom used to the end.
  * model.Row: Add methods .get(), .as_dict() and len operator (related to: #27).
  * Introduce ``behave.compat`` as compatibility layer for Python versions.

IMPROVEMENT:

  * issue #117: context.execute_steps() should also support steps with multi-line text or table
  * issue #116: SummaryReporter shows list of failing scenarios (provided by: roignac).
  * issue #112: Improvement to AmbiguousStep error diagnostics
  * issue #74:  django-behave module now available at pypi (done: 2012-10-04).
  * issue #27:  Row should support .get() to be more dict-like

FIXED:

  * issue #135: Avoid leaking globals between step modules.
  * issue #114: No blank lines when option --no-skipped is used (provided by: florentx).
  * issue #111: Comment following @wip tag results in scenario being ignored
  * issue  #83: behave.__main__:main() Various sys.exit issues
  * issue  #80: source file names not properly printed with python 3.3.0
  * issue  #62: --format=json: Background steps are missing (fixed: some time ago).

RESOLVED:

 * issue #98: Summary should include the names of the first X tests that failed (solved by: #116).


Version: 1.2.2.16 (2013-02-10)
-------------------------------------------------------------------------------

NEW:

  * "progress" formatter added (from jenisy-repo).
  * Add "issue.features/" to simplify verification/validation of issues (from jenisy-repo).

FIXED:

  * issue #107: test/ directory gets installed into site-packages
  * issue #99: Layout variation "a directory containing your feature files" is broken for running single features
  * issue #96: Sub-steps failed without any error info to help debug issue
  * issue #85: AssertionError with nested regex and pretty formatter
  * issue #84: behave.runner behave does not reliably detected failed test runs
  * issue #75: behave @list_of_features.txt is broken.
  * issue #73: current_matcher is not predictable.
  * issue #72: Using GHERKIN_COLORS caused an TypeError.
  * issue #70: JUnitReporter: Generates invalid UTF-8 in CDATA sections (stdout/stderr output) when ANSI escapes are used.
  * issue #69: JUnitReporter: Fault when processing ScenarioOutlines with failing steps
  * issue #67: JSON formatter cannot serialize tables.
  * issue #66: context.table and context.text are not cleared.
  * issue #65: unrecognized --tag-help argument.
  * issue #64: Exit status not set to 1 even there are failures in certain cases (related to: #52)
  * issue #63: 'ScenarioOutline' object has no attribute 'stdout'.
  * issue #35: "behave --format=plain --tags @one" seems to execute right scenario w/ wrong steps
  * issue #32: "behave ... --junit-directory=xxx" fails for more than 1 level

RESOLVED:

  * issue #81: Allow defining steps in a separate library.
  * issue #78: Added references to django-behave (pull-request).
  * issue #77: Does not capture stdout from sub-processes

REJECTED:

  * issue #109: Insists that implemented tests are not implemented (not reproducable)
  * issue #100: Forked package installs but won't run on RHEL.
  * issue #88: Python 3 compatibility changes (=> use 2to3 tool instead).

DUPLICATED:

  * issue #106: When path is to a feature file only one folder level usable (same as #99).
  * issue #105: behave's exit code only depends on the last scenario of the last feature (same as #95).
  * issue #95: Failed test run still returns exit code 0 (same as #84, #64).
  * issue #94: JUnit format does not handle ScenarioOutlines (same as #69).
  * issue #92: Output from --format=plain shows skipped steps in next scenario (same as #35).
  * issue #34: "behave --version" runs features, but shows no version (same as #30)



Version 1.2.2 - August 21, 2012
-------------------------------------------------------------------------------

* Fix for an error when an assertion message contains Unicode characters.
* Don't repr() the step text in snippets to avoid turning Unicode text into
  backslash hell.


Version 1.2.1 - August 19, 2012
-------------------------------------------------------------------------------

* Fixes for JSON output.
* Move summary reporter and snippet output to stderr.


Version 1.2.0 - August 18, 2012
-------------------------------------------------------------------------------

* Changed step name provided in snippets to avoid issues with the @step
  decorator.
* Use setup to create console scripts.
* Fixed installation on Windows.
* Fix ANSI escape sequences for cursor movement and text colourisation.
* Fixes for various command-line argument issues.
* Only print snippets once per unique step.
* Reworked logging capture.
* Fixes for dry-run mode.
* General fixes.


Version 1.1.0 - January 23, 2012
-------------------------------------------------------------------------------

* Context variable now contains current configuration.
* Context values can now be tested for (``name in context``) and deleted.
* ``__file__`` now available inside step definition files.
* Fixes for various formatting issues.
* Add support for configuration files.
* Add finer-grained controls for various things like log capture, coloured
  output, etc.
* Fixes for tag handling.
* Various documentation enhancements, including an example of full-stack
  testing with Django thanks to David Eyk.
* Split reports into a set of modules, add junit output.
* Added work-in-progress ("wip") mode which is useful when developing new code
  or new tests. See documentation for more details.


Version 1.0.0 - December 5, 2011
-------------------------------------------------------------------------------

* Initial release
