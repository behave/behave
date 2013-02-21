Version History
===============================================================================


Next Version 1.2.2.x - UNRELEASED
-------------------------------------------------------------------------------

IMPROVEMENT:

  * issue #116: SummaryReporter shows list of failing scenarios (provided by: roignac).
  * issue #112: Improvement to AmbiguousStep error diagnostics
  * issue #74:  django-behave module now available at pypi (done: 2012-10-04).

FIXED:

  * issue #114: No blank lines when option --no-skipped is used (provided by: florentx).
  * issue #111: Comment following @wip tag results in scenario being ignored

RESOLVED:

 * issue #98: Summary should include the names of the first X tests that failed (solved by: #116).


Version: 1.2.2.16 (2013-02-10)

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
