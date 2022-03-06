Version History
===============================================================================

Version: 1.2.7 (unreleased)
-------------------------------------------------------------------------------

BACKWARD-INCOMPATIBLE:

* Replace old-style tag-expressions with `cucumber-tag-expressions`_ as ``tag-expressions v2``.

  HINTS:

  - DEPRECATING: ``tag-expressions v1`` (old-style)
  - BUT: Currently, tag-expression version is automatically detected (and used).

GOALS:

- Improve support for Windows (continued)
- FIX: Unicode problems on Windows (in behave-1.2.6)
- FIX: Regression test problems on Windows (in behave-1.2.6)

DEVELOPMENT:

* Renamed default branch of Git repository to "main" (was: "master").
* Use github-actions as CI/CD pipeline (and remove Travis as CI).

CLEANUPS:

* Remove ``stdout_capture``, ``stderr_capture``, ``log_capture``
  attributes from ``behave.runner.Context`` class
  (use: ``captured`` attribute instead).

ENHANCEMENTS:

* Add support for Gherkin v6 grammar and syntax in ``*.feature`` files
* Use `cucumber-tag-expressions`_ with tag-matching extension (superceeds: old-style tag-expressions)
* Use cucumber "gherkin-languages.json" now (simplify: Gherkin v6 aliases, language usage)
* Support emojis in ``*.feature`` files and steps
* Select-by-location: Add support for "Scenario container" (Feature, Rule, ScenarioOutline) (related to: #391)
* pull  #988: setup.py: Add category to install additional formatters (html) (provided-by: bittner)
* pull  #895: UPDATE: i18n/gherkin-languages.json from cucumber repository #895 (related to: #827)
* pull  #827: Fixed keyword translation in Estonian #827 (provided by: ookull)
* issue #740: Enhancement: possibility to add cleanup to be called upon leaving outer context stack frames (submitted by: nizwiz, dcvmoole)
* issue #678: Scenario Outline: Support tags with commas and semicolons (provided by: lawnmowerlatte, pull #679)
* issue #675: Feature files cannot be found within symlink directories (provided by: smadness, pull #680)

CLARIFICATION:

* issue #810: Clarify select-by-name using regex pattern (submitted by: xv-chris-w)

FIXED:

* FIXED: Some tests related to python3.9
* FIXED: active-tag logic if multiple tags with same category exists.
* pull  #967: Update __init__.py in behave import to fix pylint (provided by: dsayling)
* issue #955: setup: Remove attribute 'use_2to3' (submitted by: krisgesling)
* issue #772: ScenarioOutline.Examples without table (submitted by: The-QA-Geek)
* issue #755: Failures with Python 3.8 (submitted by: hroncok)
* issue #725: Scenario Outline description lines seem to be ignored (submitted by: nizwiz)
* issue #713: Background section doesn't support description (provided by: dgou)
* pull  #657: Allow async steps with timeouts to fail when they raise exceptions (provided by: ALSchwalm)
* issue #641: Pylint errors when importing given - when - then from behave (solved by: #967)
* issue #631: ScenarioOutline variables not possible in table headings (provided by: mschnelle, pull #642)
* issue #619: Context __getattr__ should raise AttributeError instead of KeyError (submitted by: anxodio)
* pull  #588: Steps-catalog argument should not break configured rerun settings (provided by: Lego3)

MINOR:

* issue #800: Cleanups related to Gherkin parser/ParseError question (submitted by: otstanteplz)
* pull  #767: FIX: use_fixture_by_tag didn't return the actual fixture in all cases (provided by: jgentil)
* pull  #751: gherkin: Adding Rule keyword translation in portuguese and spanish to gherkin-languages.json (provided by: dunossauro)
* pull  #660: Fix minor typos (provided by: rrueth)
* pull  #655: Use pytest instead of py.test per upstream recommendation (provided by: scop)
* issue #654: tox.ini: pypi.python.org -> pypi.org (submitted by: pradyunsg)

DOCUMENTATION:

* pull  #989: Add more tutorial links: Nicole Harris, Nick Coghlan (provided by: ncoghlan, bittner; related: #848)
* pull  #877: docs: API reference - Capitalizing Step Keywords in example (provided by: Ibrian93)
* pull  #731: Update links to Django docs (provided by: bittner)
* pull  #722: DOC remove remaining pythonhosted links (provided by: leszekhanusz)
* pull  #701: behave/runner.py docstrings (provided by: spitGlued)
* pull  #700: Fix wording of "gherkin.rst" (provided by: spitGlued)
* pull  #699: Fix wording of "philosophy.rst" (provided by: spitGlued)
* pull  #684: Fix typo in "install.rst" (provided by: mstred)
* pull  #628: Changed pythonhosted.org links to readthedocs.io (provided by: chrisbrake)

BREAKING CHANGES (naming):

* behave.runner.Context._push(layer=None): Was Context._push(layer_name=None)
* behave.runner.scoped_context_layer(context, layer=None):
  Was scoped_context_layer(context.layer_name=None)


.. _`cucumber-tag-expressions`: https://pypi.org/project/cucumber-tag-expressions/


Version: 1.2.6 (2018-02-25)
-------------------------------------------------------------------------------

GOALS:

- Improve support for Windows


DOCUMENTATION:

* issue #625: Formatter documentation is inaccurate for some methods (reported by: throwable-one)
* pull  #618: Fix a typo in the background section of gherkin docs (provided by: mrrn)
* pull  #609: Describe execute_steps() behaviour correctly (provided by: mixxorz)
* pull  #603: Update typo tutorial.rst (provided by: fnaval)
* pull  #601: Add Flask integration chapter to documentation (provided by: bittner)
* pull  #580: Fix some dead ecosystem links (provided by: smadness)
* pull  #579: Add explanation for step_impl function name (provided by: bittner)
* issue #574: flake8 reports F811 redefinition of unused 'step_impl' (fixed by #579).
* pull  #545: Spell "section" correctly (provided by: chelmertz)
* pull  #489: Fix link to Selenium docs in Django chapter (provided by: bittner)
* pull  #469: Fix typo in "formatters.rst" (provided by: ab9-er)
* pull  #443: Fixing grammar in philosophy.rst (provided by: jamesroutley)
* pull  #441: Integrate hint on testing more nicely (provided by: bittner)
* pull  #429: Replace "Manual Integration" by "Automation Libraries" section (provided by: bittner)
* pull  #379: Correct wording in README.rst (provided by: franklinchou)
* pull  #362: docs/tutorial.rst: fixed non-monospace font (provided by: spacediver)
* pull  #359: Update documentation related to Django (behave-django) (provided by: bittner)
* pull  #326: docs/tutorial.rst: Correct features directory path creation (provided by: memee)
* issue #356: docs/api.rst: type in implementation (submitted by: tomxtobin)
* pull  #335: docs/api.rst: execute_steps() example (provided by: miabbott)
* pull  #339: Adapt wording in install.rst (provided by: charleswhchan)
* pull  #338: docs/philosophy.rst: Correct to uppercase in example (provided by: charleswhchan)
* issue #323: Update Django Example to work with version >=1.7 (submitted by: mpetyx, provided by: bittner)
* pull  #327: Fix typo in Django doc (provided by: nikolas)
* pull  #321: Update Django integration (provided by: bittner, contains: #315, #316)
* FIX: cmdline/config-param doc-generator, avoid duplicated param entries (related to: #318)
* issue #317: Update comparison: lettuce tags (provided by: ramiabughazaleh)
* pull  #307: Typo in readme (provided by: dflock)
* pull  #305: behave.rst related fixes reapplied (provided by: bittner)
* pull  #292: Use title-cased keywords in tutorial scenario (provided by: neoblackcap)
* pull  #291: Tiny tweaks in tutorial docs (provided by: bernardpaulus)

SITE:

* pull #626: Formatting issue in stale-bot config (provided by: teapow)
* pull #343: Update/fix badges in README (provided by: mixxorz)

ENHANCEMENTS:

* fixtures: Add concept to simplify setup/cleanup tasks for scenario/feature/test-run
* context-cleanups: Use context.add_cleanup() to perform cleanups after scenario/feature/test-run.
* Tagged Examples: Examples in a ScenarioOutline can now have tags.
* pull  #596: Add missing Czech translation (provided by: hason)
* pull  #554: Adds galician language (provided by: carlosgoce)
* pull  #447: behave settings from tox.ini (provided by: bittner)
* issue #411: Support multiple active-tags with same category (submitted by: Kani999)
* issue #409: Support async/@asyncio.coroutine steps (submitted by: dcarp)
* issue #357: Add language attribute to Feature class
* pull  #328: Auto-retry failed scenarios in unreliable environment (provided by: MihaiBalint, robertknight)
* issue #302: Support escaped-pipe in Gherkin table cell value (provided by: connorsml, pull #360)
* issue #301: Support default tags in configfile
* issue #299: Runner can continue after a failed step (same as: #314)
* issue #197: Hooks processing should be more exception safe (provided by: vrutkovs, jenisys, pull #205)

FORMATTERS:

* pull  #446: Remove Formatter scenario_outline(), examples() method (provided by:  aisbaa, jenisys)
* pull  #448: json: Add status to scenarios in JSON report (provided by: remcowesterhoud)
* issue #462: json: Invalid JSON output when no features are selected (submitted by: remcowesterhoud)
* pull  #423: sphinx.steps: Support ref link for each step (provided by: ZivThaller)
* pull  #460: pretty: Print the step implementation location when dry-run (provided by: unklhe, jenisys)

REPORTERS:

* junit: Add timestamp and hostname attributes to testsuite XML element.
* junit: Support to tweak output with userdata (experimental).
* junit: Support scenario hook-errors with JUnitReporter (related to: #466)

CHANGES:

* status: Use Status enum-class for feature/scenario/step.status (was: string)
* hook-processing: Skips now feature/scenario/step if before-hook fails (related to: #454)
* parser: language comment in feature file has higher priority than --lang option (related to: #334).
* issue #385: before_scenario/before_feature called too late (submitted by: BRevzin)

FIXED:

* issue #606: Using name option w/ special unicode chars (submitted by: alluir42)
* issue #547: Crash when using step definition with optional cfparse parts (provided by: ftartaggia, jenisys)
* pull  #599: Steps from another Windows drive (provided by: psicopep)
* issue #582: behave emitting PendingDeprecationWarning messages (submitted by: adamjcooper)
* pull  #476: scenario.status when scenario without steps is skipped (provided by: ar45, jenisys)
* pull  #471: convert an object to unicode (py2) using __unicode__ method first  unicode (provided by: ftartaggia)
* issue #458: UnicodeEncodeError inside naked except block in __main__.py (submitted by: mseery)
* issue #453: Unicode chars are broken in stacktrace (submitted by: throwable-one)
* issue #455: Restore backward compatibility to Cucumber style RegexMatcher (submitted by:  avabramov)
* issue #449: Unicode is processed incorrectly for Py2 in "textutil.text" (submitted by: throwable-one)
* issue #446: after_scenario HOOK-ERROR asserts with jUnit reporter (submitted by: lagin)
* issue #424: Exception message with unicode characters in nested steps (submitted by: yucer)
* issue #416: JUnit report messages cut off (submitted by: remcowesterhoud, provided by: bittner)
* issue #414: Support for Jython 2.7 (submitted by: gabtwi...)
* issue #384: Active Tags fail with ScenarioOutline (submitted by: BRevzin)
* issue #383: Handle (custom) Type parsing errors better (submitted by: zsoldosp)
* pull  #382: fix typo in tag name (provided by: zsoldosp)
* issue #361: utf8 file with BOM (provided by: karulis)
* issue #349: ScenarioOutline skipped with --format=json
* issue #336: Stacktrace contents getting illegal characters inserted with text function (submited by: fj40bryan)
* issue #330: Skipped scenarios are included in junit reports when --no-skipped is specified (provided by: vrutkovs, pull #331)
* issue #320: Userdata is case-insensitive when read from config file (provided by: mixxorz)
* issue #319: python-version requirements in behave.whl for Python2.6 (submitted by: darkfoxprime)
* issue #310: Use setuptools_behave.py with behave module
* issue #309: behave --lang-list fails on Python3 (and Python2)
* issue #300: UnicodeDecodeError when read steps.py (similar to: #361)
* issue #288: Use print function instead print statement in environment/steps files


Version: 1.2.5 (2015-01-31)
-------------------------------------------------------------------------------

:Same as: Version 1.2.5a1 (unreleased).

NEWS and CHANGES:

  - General:

    * Improve support for Python3 (py3.3, py3.4; #268)
    * Various unicode related fixes (Unicode errors with non-ASCII, etc.)
    * Drop support for Python 2.5

  - Running:

    * ScenarioOutline: Annotates name with row.id, ... to better represent row.
    * NEW: Active Tags, see docs (`New and Noteworthy`_).
    * NEW: Test stages, see docs (`New and Noteworthy`_).
    * NEW: User-specific configuration data, see docs (`New and Noteworthy`_).
    * CHANGED: Undefined step snippet uses now NotImplementedError (related to: #254)

  - Model:

    * ScenarioOutline: Various improvements, see docs (`New and Noteworthy`_).

  - Formatters:

    * plain: Can now show tags, but currently disabled per default
    * NEW: steps.catalog: Readable summary of all steps (similar to: steps.doc, #271)
    * NEW: User-defined formatters, see docs (`New and Noteworthy`_).

ENHANCEMENTS:

  * pull #285: Travis CI improvements to use container environment, etc. (provided by: thedrow)
  * pull #272: Use option role to format command line arg docs (provided by: helenst)
  * pull #271: Provide steps.catalog formatter (provided by: berdroid)
  * pull #261: Support "setup.cfg" as configuration file, too (provided by: bittner)
  * pull #260: Documentation tweaks and typo fixes (provided by: bittner)
  * pull #254: Undefined step raises NotImplementedError instead of assert False (provided by: mhfrantz)
  * issue #242: JUnitReporter can show scenario tags (provided by: rigomes)
  * issue #240: Test Stages with different step implementations (provided by: attilammagyar, jenisys)
  * issue #238: Allow to skip scenario in step function (provided by: hotgloupi, jenisys)
  * issue #228: Exclude scenario fron run (provided by: jdeppe, jenisys)
  * issue #227: Add a way to add command line options to behave (provided by: attilammagyar, jenisys)

FIXED:

  * pull  #283: Fix "fork me" image in docs (provided by: frodopwns)
  * issue #280: Fix missing begin/end-markers in RegexMatcher (provided by: tomekwszelaki, jenisys)
  * pull  #268: Fix py3 compatibility with all tests passed (provided by: sunliwen)
  * pull  #252: Related to #251 (provided by: mcepl)
  * pull  #190: UnicodeDecodeError in tracebacks (provided by: b3ni, vrutkovs, related to: #226, #230)
  * issue #257: Fix JUnitReporter (XML) for Python3 (provided by: actionless)
  * issue #249: Fix a number of docstring problems (provided by: masak)
  * issue #253: Various problems in PrettyFormatter.exception()
  * issue #251: Unicode crash in model.py (provided by: mcepl, jenisys)
  * issue #236: Command line docs are confusing (solved by: #272)
  * issue #230: problem with assert message that contains ascii over 128 value (provided by: jenisys)
  * issue #226: UnicodeDecodeError in tracebacks (provided by: md1023, karulis, jenisys)
  * issue #221: Fix some PY2/PY3 incompatibilities (provided by: johbo)
  * pull  #219: IDE's unknown modules import issue (provided by: xbx)
  * issue #216: Using --wip option does not disable ANSI escape sequences (coloring).
  * issue #119: Python3 support for behave (solved by: #268 and ...)
  * issue #82:  JUnitReporter fails with Python 3.x (fixed with: #257, #268)


.. _`New and Noteworthy`: https://github.com/behave/behave/blob/master/docs/new_and_noteworthy.rst


Version: 1.2.4 (2014-03-02)
-------------------------------------------------------------------------------

:Same as: Version 1.2.4a1 (unreleased).

NEWS and CHANGES:

  - Running:

    * ABORT-BY-USER: Better handle KeyboardInterrupt to abort a test run.
    * feature list files (formerly: feature configfiles) support wildcards.
    * Simplify and improve setup of logging subsystem (related to: #143, #177)

  - Step matchers:

    * cfparse: Step matcher with "Cardinality Field" support (was: optional).

  - Formatters:

    * steps.usage: Avoid duplicated steps usage due to Scenario Outlines.
    * json: Ensures now that matched step params (match args) cause valid JSON.


IMPROVEMENT:

  * issue #108: behave.main() can be called with command-line args (provided by: medwards, jenisys)
  * issue #172: Subfolders in junit XML filenames (provided by: roignac).
  * issue #203: Integration with pdb (debug on error; basic support)
  * Simple test runner to run behave tests from "setup.py"

FIXED:

  * issue #143: Logging starts with a StreamHandler way too early (provided by: jtatum, jenisys).
  * issue #175: Scenario isn't marked as 'failed' when Background step fails
  * issue #177: Cannot setup logging_format
  * issue #181: Escape apostrophes in undefined steps snippets
  * issue #184: TypeError when running behave with --include option (provided by: s1ider).
  * issue #186: ScenarioOutline uses wrong return value when if fails (provided by: mdavezac)
  * issue #188: Better diagnostics if nested step is undefined
  * issue #191: Using context.execute_steps() may change context.table/.text
  * issue #194: Nested steps prevent that original stdout/stderr is restored
  * issue #199: behave tag expression bug when or-not logic is used


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
