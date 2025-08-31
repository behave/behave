.. _id.noteworthy_in_version_1.2.7:

Noteworthy in Version 1.2.7
==============================================================================

Summary:

* Support `Gherkin v6 grammar`_ (to simplify usage of `Example Mapping`_)
* Use/Support :pypi:`cucumber-tag-expressions` (supersedes: old-style tag-expressions)
* :pypi:`cucumber-tag-expressions` are extended by "tag-matching"
  to match partial tag names, like: ``@foo.*``
* `Select-by-location for Scenario Containers`_ (Feature, Rule, ScenarioOutline)
* `Support for emojis in feature files and steps`_
* `Extension Point: Runner`_
* `Improve Active-Tags Logic`_
* `Active-Tags: Use ValueObject for better Comparisons`_
* `Detect bad step definitions`_
* `Distinguish between Failures and Errors`_
* `Support for Pending Steps`_
* `Step definitions with Cucumber-Expressions`_
* `Improved Logging Support`_
* `Improved Capture Support`_
* `Step Decorators: Support for Async-Steps`_

BREAKING CHANGES:

* `Gherkin Parser strips no longer trailing colon from step`_
* Capture related command line options changed (some in incompatible ways).

.. _`Example Mapping`: https://cucumber.io/blog/bdd/example-mapping-introduction/
.. _`Example Mapping Webinar`: https://cucumber.io/blog/bdd/example-mapping-webinar/
.. _`Gherkin v6 grammar`: https://github.com/cucumber/gherkin/blob/main/gherkin.berp



Support Gherkin v6 Grammar
-------------------------------------------------------------------------------

Grammar changes:

* ``Rule`` concept added to better correspond to `Example Mapping`_ concepts
* Add aliases for ``Scenario`` and ``Scenario Outline`` (for similar reasons)

.. code-block::
    :caption: FEATURE GRAMMAR (PSEUDO-CODE)

    @tag1 @tag2
    Feature: Optional Feature Title...

        Description?        #< CARDINALITY: 0..1 (optional)
        Background?         #< CARDINALITY: 0..1 (optional)
        Scenario*           #< CARDINALITY: 0..N (many)
        ScenarioOutline*    #< CARDINALITY: 0..N (many)
        Rule*               #< CARDINALITY: 0..N (many)

A Rule (or: business rule) allows to group multiple Scenario(s)/Example(s):

.. code-block::
    :caption: RULE GRAMMAR (PSEUDO-CODE)

    @tag1 @tag2
    Rule: Optional Rule Title...

        Description?        #< CARDINALITY: 0..1 (optional)
        Background?         #< CARDINALITY: 0..1 (optional)
        Scenario*           #< CARDINALITY: 0..N (many)
        ScenarioOutline*    #< CARDINALITY: 0..N (many)


Gherkin v6 keyword aliases:

==================  =================== ======================
Concept             Preferred Keyword   Alias(es)
==================  =================== ======================
Scenario            Example             Scenario
Scenario Outline    Scenario Outline    Scenario Template
Examples            Examples            Scenarios
==================  =================== ======================


EXAMPLE:

.. code-block:: gherkin
    :caption: FILE: features/example_with_rules.feature

    # -- USING: Gherkin v6
    Feature: With Rules

      Background: Feature.Background
        Given feature background step_1

      Rule: Rule_1
        Background: Rule_1.Background
          Given rule_1 background step_1

        Example: Rule_1.Example_1
          Given rule_1 scenario_1 step_1

      Rule: Rule_2

        Example: Rule_2.Example_1
          Given rule_2 scenario_1 step_1

      Rule: Rule_3
        Background: Rule_3.EmptyBackground
        Example: Rule_3.Example_1
          Given rule_3 scenario_1 step_1

Overview of the `Example Mapping`_ concepts:

.. image:: _static/Cucumber_ExampleMapping.png
    :scale: 50 %
    :alt: Cucumber: `Example Mapping`_


.. seealso::

    **Gherkin v6**:

    * https://docs.cucumber.io/gherkin/reference/
    * `Gherkin v6 grammar`_

    **Example Mapping:**

    * Cucumber: Introduction to `Example Mapping`_ (by: Matt Wynne)
    * Cucumber: `Example Mapping Webinar`_
    * https://docs.cucumber.io/bdd/example-mapping/

    **More on Example Mapping:**

    * https://speakerdeck.com/mattwynne/rules-vs-examples-bddx-london-2014
    * https://lisacrispin.com/2016/06/02/experiment-example-mapping/
    * https://tobythetesterblog.wordpress.com/2016/05/25/how-to-do-example-mapping/

.. hint:: **Gherkin v6 Grammar Issues**

    * :cucumber.issue:`632`: Rule tags are currently only supported in `behave`.
      The Cucumber Gherkin v6 grammar currently lacks this functionality.

    * :cucumber.issue:`590`: Rule Background:
      A proposal is pending to remove Rule Backgrounds again


.. include:: _content.tag_expressions_v2.rst


Select-by-location for Scenario Containers
-------------------------------------------------------------------------------

In the past, it was already possible to scenario(s) by using its **file-location**.

A **file-location** has the schema: ``<FILENAME>:<LINE_NUMBER>``.
Example: ``features/alice.feature:12``
(refers to ``line 12`` in ``features/alice.feature`` file).

Rules to select **Scenarios** by using the file-location:

* **Scenario:** Use a file-location that points to the keyword/title or its steps
  (until next Scenario/Entity starts).

* **Scenario of a ScenarioOutline:**
  Use the file-location of its Examples row.

Now you can select all entities of a **Scenario Container** (Feature, Rule, ScenarioOutline):

* **Feature:**
  Use file-location before first contained entity/Scenario starts.

* **Rule:**
  Use file-location from keyword/title line to line before its first Scenario/Background.

* **ScenarioOutline:**
  Use file-location from keyword/title line to line before its Examples rows.

A file-location into a **Scenario Container** selects all its entities
(Scenarios, ...).


Support for Emojis in Feature Files and Steps
-------------------------------------------------------------------------------

* Emojis can now be used in ``*.feature`` files.
* Emojis can now be used in step definitions.
* You can now use ``language=emoji (em)`` in ``*.feature`` files ;-)

.. literalinclude:: ../features/i18n_emoji.feature
    :caption: FILE: features/i18n_emoji.feature
    :language: gherkin

.. literalinclude:: ../features/steps/i18n_emoji_steps.py
    :caption: FILE: features/steps/i18n_emoji_steps.py
    :language: python


Extension Point: Runner
-------------------------------------------------------------------------------

:pypi:`behave` has now an extension point to supply an own test runner.
See :ref:`id.appendix.runners` for more details.


Improve Active-Tags Logic
-------------------------------------------------------------------------------

The active-tag computation logic was slightly changed (and fixed):

* if multiple active-tags with same category are used
* combination of positive active-tags (``use.with_{category}={value}``) and
  negative active-tags (``not.with_{category}={value}``) with same category
  are now supported

All active-tags with same category are combined into one category tag-group.
The following logical expression is used for active-tags with the same category:

.. code-block::
    :caption: ALGORITHM: Active-Tag Expressions

    category_tag_group.enabled := positive-tag-group-expression and not negative-tag-group-expression
    positive-tag-group-expression := enabled(tag1) or enabled(tag2) or ...
    negative-tag-group-expression := enabled(tag3) or enabled(tag4) or ...

    enabled(tag) := TRUE, if positive/negative active-tag condition is TRUE.
    POSITIVE TAGS: tag1, tag2  --  @use.with_{category}={value}
    NEGATIVE TAGS: tag3, tag4  --  @not.with_{category}={value}


EXAMPLE:

.. code-block:: gherkin
    :caption: FILE: features/active_tag.example.feature

    Feature: Active-Tag Example

      @use.with_browser=Safari
      @use.with_browser=Chrome
      @not.with_browser=Firefox
      Scenario: Use one active-tag group/category

        HINT: Only executed with web browser Safari and Chrome, Firefox is explicitly excluded.
        ...

      @use.with_browser=Firefox
      @use.with_os=linux
      @use.with_os=darwin
      Scenario: Use two active-tag groups/categories

        HINT 1: Only executed with browser: Firefox
        HINT 2: Only executed on OS: Linux and Darwin (macOS)
        ...


Active-Tags: Use ValueObject for better Comparisons
-------------------------------------------------------------------------------

The current mechanism of active-tags only supports the ``equals / equal-to`` comparison
mechanism to determine if the ``tag.value`` matches the ``current.value``, like:

.. code-block:: gherkin
    :caption: NAME SCHEMA FOR: Active-tags

    # -- SCHEMA: "@use.with_{category}={value}" or "@not.with_{category}={value}"
    @use.with_browser=Safari    # HINT: tag.value = "Safari"
    @not.with_browser=Safari    # HINT: tag.value = "Safari"

    ACTIVE TAG MATCHES, if:
        current.value == tag.value  (using "@use..." for string values)
        current.value != tag.value  (using "@not..." for string values)

The ``equals-to`` comparison method is sufficient for many situations.
But in some situations, you want to use other comparison methods.
The ``behave.tag_matcher.ValueObject`` class was added to allow
the user to provide an own comparison method (and type conversion support).

**EXAMPLE 1:**

.. code-block:: gherkin
    :caption: FILE: features/active_tags.example1.feature

    Feature: Active-Tag Example 1 with ValueObject

      @use.with_temperature.min_value=15
      Scenario: Only run if temperature >= 15 degrees Celsius
        ...

.. code-block:: python
    :caption: FILE: features/environment.py

    import operator
    from behave.tag_matcher import ActiveTagMatcher, ValueObject
    from my_system.sensors import Sensors

    # -- SIMPLIFIED: Better use behave.tag_matcher.NumberValueObject
    # CTOR: ValueObject(value, compare=operator.eq)
    # HINT: Parameter "value" can be a getter-function (w/o args).
    class NumberValueObject(ValueObject):
        def matches(self, tag_value):
            tag_number = int(tag_value)
            return self.compare(self.value, tag_number)

    current_temperature = Sensors().get_temperature()
    active_tag_value_provider = {
        # -- COMPARISON:
        # temperature.value:     current.value == tag.value  -- DEFAULT: equals  (eq)
        # temperature.min_value: current.value >= tag.value  -- greater_or_equal (ge)
        "temperature.value":     NumberValueObject(current_temperature),
        "temperature.min_value": NumberValueObject(current_temperature, operator.ge),
    }
    active_tag_matcher = ActiveTagMatcher(active_tag_value_provider)

    # -- HOOKS SETUP FOR ACTIVE-TAGS: ... (omitted here)


**EXAMPLE 2:**

A slightly more complex situation arises, if you need to constrain the
execution of an scenario to a temperature range, like:

.. code-block:: gherkin
    :caption: FILE: features/active_tags.example2.feature

    Feature: Active-Tag Example 2 with Min/Max Value Range

      @use.with_temperature.min_value=10
      @use.with_temperature.max_value=70
      Scenario: Only run if temperature is between 10 and 70 degrees Celsius
        ...

.. code-block:: python
    :caption: FILE: features/environment.py

    ...
    current_temperature = Sensors().get_temperature()
    active_tag_value_provider = {
        # -- COMPARISON:
        # temperature.min_value:  current.value >= tag.value
        # temperature.max_value:  current.value <= tag.value
        "temperature.min_value": NumberValueObject(current_temperature, operator.ge),
        "temperature.max_value": NumberValueObject(current_temperature, operator.le),
    }
    ...

**EXAMPLE 3:**

.. code-block:: gherkin
    :caption: FILE: features/active_tags.example3.feature

    Feature: Active-Tag Example 3 with Contains/Contained-in Comparison

      @use.with_supported_payment_method=VISA
      Scenario: Only run if VISA is one of the supported payment methods
        ...

      # OR: @use.with_supported_payment_methods.contains_value=VISA

.. code-block:: python
    :caption: FILE: features/environment.py

    # -- NORMALLY:
    #  from my_system.payment import get_supported_payment_methods
    #  payment_methods = get_supported_payment_methods()
    ...
    payment_methods = ["VISA", "MasterCard", "paycheck"]
    active_tag_value_provider = {
        # -- COMPARISON:
        # supported_payment_method: current.value contains tag.value
        "supported_payment_method": ValueObject(payment_methods, operator.contains),
    }
    ...


Detect Bad Step Definitions
-------------------------------------------------------------------------------

The **regular expression** (:mod:`re`) module in Python has increased the checks
when bad regular expression patterns are used. Since `Python >= 3.11`,
an :class:`re.error` exception may be raised on some regular expressions.
The exception is raised when the bad regular expression is compiled
(on :func:`re.compile()`).

``behave`` has added the following support:

* Detects a bad step-definition when they are added to the step-registry.
* Reports a bad step-definition and their exception during this step.
* bad step-definitions are not registered in the step-registry.
* A bad step-definition is like an UNDEFINED step-definition.
* A :class:`~behave.formatter.bad_steps.BadStepsFormatter` formatter was added that shows any BAD STEP DEFINITIONS


.. note:: More Information on BAD STEP-DEFINITIONS:

    * :this_repo:`features/formatter.steps_bad.feature`
    * :this_repo:`features/runner.bad_steps.feature`


Gherkin Parser strips no longer trailing colon from step
-------------------------------------------------------------------------------

In the past, the Gherkin parser removed a trailing colon (`:`) on steps
that had a text or table section.

EXAMPLE:

.. code-block:: gherkin
    :caption: FILE: features/parser_example.feature

    Feature:
      Scenario:
        Given a file named "some_file.txt" with:
          """
          Lorem ipsum, ipsum lorem, ...
          """

.. code-block:: python
    :caption: FILE: features/steps/filesystem_steps.py

    # -- OLD IMPLEMENTATION:
    from behave import given, when, then
    from pathlib import Path

    @given('a file named "{filename}" with')  #< HINT: Ends without colon
    def step_write_file_with_contents(ctx, filename):
        Path(filename).write_text(ctx.text, encoding="UTF-8")

The behaviour of the Gherkin parser was changed:

* Trailing colon character is no longer removed on steps with text/table section

REASONS:

* The new behaviour is more natural and much simpler.
* The step writer can define whatever is needed.
* Fixes a problem in PyCharm IDE where the lookup of the step-definition in such a case is not working.

EXAMPLE 2:

.. code-block:: python
    :caption: FILE: features/steps/filesystem_steps.py

    # -- NEW IMPLEMENTATION:
    from behave import given, when, then
    from pathlib import Path

    @given('a file named "{filename}" with:')  #< HINT: Ends with colon
    def step_write_file_with_contents(ctx, filename):
        Path(filename).write_text(ctx.text, encoding="UTF-8")

.. hint::

    The old behaviour of the Gherkin parser can be (re-)enabled
    by setting the following environment variable before using `behave`_:

    .. code-block:: bash
        :caption: On UNIX: Using bash shell

        export BEHAVE_STRIP_STEPS_WITH_TRAILING_COLON="yes"

    .. code-block:: shell
        :caption: On WINDOWS: Using cmd shell

        set BEHAVE_STRIP_STEPS_WITH_TRAILING_COLON="yes"


Distinguish between Failures and Errors
-------------------------------------------------------------------------------

`behave`_ distinguishes now between failures and errors:

* a **failure** is caused by an assert-mismatch (or: :class:`AssertionError` is raised)
* an **error** is caused normally when an "unexpected" exception is caught.

In addition, an **error** occurs if:

* a hook error occurs
* a cleanup error occurs (and is not ignored)
* a pending step is detected (:class:`behave.api.pending_step.StepNotImplementedError`)
* a undefined step is detected


Support for Pending Steps
-------------------------------------------------------------------------------

`behave` provides now better support for **pending steps**.

* A pending step has a binding between the step-pattern and its step-function.
* Therefore, a pending step registers itself in the step registry
* But a pending step is not yet implemented
  (marked-by: :class:`behave.api.pending_step.StepNotImplementedError` )

A **pending step** looks like:

.. code-block:: python
    :caption: FILE: features/steps/pending_step_example.py

    from behave import given, when, then
    from behave.api.pending_step import StepNotImplementedError

    @given('a pending step')
    def step_given_a_pending_step(ctx):
        raise StepNotImplementedError("Given a pending step")

A pending step causes an error during the test run.
But you can mark a scenario temporarily with the `@wip` tag
to let any of its pending steps pass:

.. code-block:: gherkin
    :caption: FILE: features/pending_step.feature

    Feature: Example

      @wip
      Scenario: With @wip tag and pending step
        Given a step passes
        When a pending step is used
        Then another step passes

.. code-block:: bash
    :caption: shell: Run behave tests

    $ behave -f plain features/pending_step.feature
    Feature: Example

      Scenario: With @wip tag and pending step
        Given a step passes ... passed
        When a pending step is used ... pending_warn
        When another step passes ... passed

    ...
    1 scenario passed, 0 failed, 0 skipped
    2 steps passed, 0 failed, 0 skipped, 1 pending_warn

Without the `@wip` marker, a scenario with pending steps causes an error:

.. code-block:: bash
    :caption: shell: Run behave tests

    $ behave -f plain features/other_pending_step.feature
    Feature: Example 2

      Scenario: Without @wip tag but with pending step
        Given a step passes ... passed
        When a pending step is used ... pending

    ...
    0 scenarios passed, 0 failed, 1 error, 0 skipped
    1 step passed, 0 failed, 1 skipped, 1 pending


.. note:: More Information on **pending steps** and **undefined steps**:

    * :this_repo:`features/step.pending_steps.feature`
    * :this_repo:`features/step.undefined_steps.feature`


Step Definitions with Cucumber-Expressions
-------------------------------------------------------------------------------

Support for a step definitions with `cucumber-expressions`_ was added to `behave`_
by providing the :mod:`behave.cucumber_expression` module.

`Cucumber-expressions`_:

* Provide a simple syntax for step-parameters (aka: placeholders) compared to regular-expressions
* Provide a simple syntax for optional or alternative (unmatched) text parts.
* Provide support for parameter types and type conversions
* Provide a number of predefined parameter types, like: ``{int}``, ``{word}``, ``{string}``, ...
* Similar to ``parse-expressions`` that are normally used in `behave`_
  (hint: ``parse-expressions`` was one of the descendants that lead to the development of `cucumber-expressions`_)


**EXAMPLE 1:**

Use the :func:`use_step_matcher_for_cucumber_expressions() <behave.cucumber_expression.use_step_matcher_for_cucumber_expressions()>`
function to enable this step-matcher before any step definitions with `cucumber-expressions`_ are used.
It is possible to do this:

* in the ``features/environment.py`` file (as default step-matcher)
* in each ``features/steps/*.py`` steps file

.. literalinclude:: ../examples/cucumber-expressions/features/environment.py
    :caption: FILE: features/environment.py


In this example, we want to use the :class:`Color <example4me.color.Color>` enum as ``parameter_type`` (placeholder)
in the steps definitions:

.. literalinclude:: ../examples/cucumber-expressions/example4me/color.py
    :caption: FILE: example4me/color.py


We provide the necessary steps with the additional ``parameter_type=color``
by using the ``Color.from_name()`` function as type converter/transformer.

.. literalinclude:: ../examples/cucumber-expressions/features/steps/color_steps.py
    :caption: FILE: features/steps/color_steps.py
    :end-before:  # -- STEP DEFINITIONS:
    :append: ...


After the ``parameter_type=color`` is defined, we can use it as ``{color}`` placeholder
in the step definitions:

.. literalinclude:: ../examples/cucumber-expressions/features/steps/color_steps.py
    :caption: FILE: features/steps/color_steps.py (continued)
    :prepend:
        # -- STEP DEFINITIONS:
    :start-after:  # -- STEP DEFINITIONS:


.. literalinclude:: ../examples/cucumber-expressions/features/cucumber_expression.feature
    :caption: FILE: features/cucumber_expression.feature
    :language: gherkin


**EXAMPLE 2: Use TypeBuilder.make_enum()**

The solution in "EXAMPLE 1" can be simplified by using the :class:`TypeBuilder <behave.cucumber_expression.TypeBuilder>` class.
It provides a :func:`TypeBuilder.make_enum()` that generates a ``parse-function`` for an :class:`Enum` class or a dict-mapping.
This ``parse-function`` provides a type converter/transformer and its regular-expression pattern (as attribute), like:

.. literalinclude:: ../examples/cucumber-expressions/features/steps/color_steps2.py.disabled
    :language: python
    :caption: FILE: features/steps/color_steps.py (ALTERNATIVE)
    :emphasize-lines: 9,14,16
    :end-before: # -- STEP DEFINITIONS:
    :append: ...


**MORE:**

In addition, the :class:`TypeBuilder <behave.cucumber_expression.TypeBuilder>` class
provides support to compose ``parse-functions`` (aka: type converters)
and regular-expression patterns from other ``parse-functions`` or data, like:

* :func:`TypeBuilder.make_enum() <behave.cucumber_expression.TypeBuilder.make_enum()>`:
  Builds a ``parse-function`` and regex-pattern for an :class:`Enum <enum.Enum>` class
  or a key/value mapping (aka: :class:`dict`).

* :func:`TypeBuilder.make_choice() <behave.cucumber_expression.TypeBuilder.make_choice()>`:
  Builds a ``parse-function`` and regex-pattern for a list of string values.

* :func:`TypeBuilder.make_variant() <behave.cucumber_expression.TypeBuilder.make_variant()>`:
  Builds a ``parse-function`` and regex-pattern from a list of
  ``parse-functions`` (and their patterns) as alternative types.

* :func:`TypeBuilder.with_many() <behave.cucumber_expression.TypeBuilder.with_many()>`:
  Builds a ``parse-function`` and regex-pattern for **many items** based on the
  ``parse-function`` of one item


.. seealso:: `cucumber-expressions`_

    * Repository: https://github.com/cucumber/cucumber-expressions
    * :this_repo:`features/step_matcher.cucumber_expressions.feature`

.. seealso:: parse-expressions

    * :pypi:`parse`
    * :pypi:`parse-type` (and :class:`TypeBuilder <behave.cucumber_expression.TypeBuilder>` core functionality)

.. note::

    A ``parameter_type`` can only be defined once (maybe: Use the ``environment-file`` or ...).


.. _`cucumber-expressions`: https://github.com/cucumber/cucumber-expressions


Improved Logging Support
-------------------------------------------------------------------------------

It is now simpler to set up the logging to a file in `behave`:

.. code-block:: python
    :caption: FILE: features/environment.py

    def before_all(ctx):
        log_format = "LOGFILE.{levelname} -- {name}: {message}"
        ctx.config.setup_logging(filename="behave.log", format=log_format)

    # -- NOTE: Setup with logging configuration file was needed before.

.. tip::

    `behave`_ supports now the newer, additional format styles for log record formats:

    * f-string format style, like: ``{message}``
    * shell placeholder format style, like: ``${message}``

    Only the percent-string placeholder style was supported before (like: ``%(message)s``).

.. seealso::

    * :this_repo:`features/logging.to_file.feature`
    * :this_repo:`features/logging.setup_with_configfile.feature`
    * :python.docs:`howto/logging-cookbook.html#use-of-alternative-formatting-styles`


Improved Capture Support
-------------------------------------------------------------------------------

The capture of hooks is now supported (special case: ``before_all()`` hook).
To better support this, the formatter(s) are now called before the
``before_feature/before_scenario/before_tag`` hooks are called.
This ensures that the Feature/Scenario name is shown (as context)
before the any captured output of ``before_feature/before_scenario/before_tag`` hooks
is printed.

AFFECTED FORMATTERS:

* pretty
* plain

.. seealso::

    * :this_repo:`features/capture.on_hooks.feature`
    * :this_repo:`features/runner.hook_errors.feature`
    * :this_repo:`features/runner.context_cleanup.feature`


**CHANGES** (partly incompatible):

The name of capture related command line options have been changed slightly:

====================== ===================== =======================================================
Option Name             Old Option Name      Description
====================== ===================== =======================================================
``--capture``           ---                  NEW: Enable/disable capture mode for stdout/stderr/log.
``--capture-hooks``     ---                  NEW: Enable/disable capture of hooks.
``--capture-stdout``    ``--capture``        Enable/disable capture of stdout.
``--capture-stderr``    ``--capture-stderr`` Enable/disable capture of stderr.
``--capture-log``       ``--logcapture``     Enable/disable capture of log-output.
====================== ===================== =======================================================

The :class:`~behave.configuration.Configuration` class attribute names were adapted
accordingly to better correspond to the command line options:

====================== ===================== =======================================================
Attribute Name         Old Attribute Name    Description
====================== ===================== =======================================================
``capture``            ---                   NEW: Enable/disable capture mode for stdout/stderr/log.
``capture_hooks``      ---                   NEW: Enable/disable capture of hooks.
``capture_stdout``     ``stdout_capture``    Enable/disable capture mode for stdout.
``capture_stderr``     ``stderr_capture``    Enable/disable capture mode for stderr.
``capture_log``        ``log_capture``       Enable/disable capture mode for log output.
====================== ===================== =======================================================

The :class:`~behave.capture.CaptureController` class attribute names were renamed
accordingly to better correspond to the naming scheme:

====================== ===================== =======================================================
Attribute Name         Old Attribute Name    Description
====================== ===================== =======================================================
``capture_stdout``     ``stdout_capture``    Used to capture stdout output.
``capture_stderr``     ``stderr_capture``    Used to capture stderr output.
``capture_log``        ``log_capture``       Used to capture log output.
====================== ===================== =======================================================

.. note::

    A deprecating warning will be emitted if you use the old names.


Step Decorators: Support for Async-Steps
-------------------------------------------------------------------------------

To simplify usage, the normal step decorators directly support async-steps now, like:

.. code-block:: python
    :caption: FILE: features/steps/async_steps.py

    # -- NOW:
    import asyncio
    from behave import given, when, then, step

    @step('a coroutine step waits "{duration:f}" seconds')
    async def step_coroutine_waits_seconds(ctx, duration: float):
        await asyncio.sleep(duration)

    @when('I execute the long running command', timeout=20.0)
    async def step_execute_long_running_command(ctx):
        # -- HINT: Step fails if step duration exceeds 20 seconds.
        pass  # ...

.. code-block:: python
    :caption: FILE: features/steps/async_steps_before.py

    # -- BEFORE:
    import asyncio
    from behave import step
    from behave.api.async_step import async_run_until_complete

    @step('a coroutine step waits "{duration:f}" seconds')
    @async_run_until_complete
    async def step_async_step_waits_seconds(ctx, duration: float):
        await asyncio.sleep(duration)

    @when('I execute the long running command')
    @async_run_until_complete(timeout=20.0)
    async def step_execute_long_running_command(ctx):
        # -- HINT: Fails if step duration exceeds 20 seconds.
        pass  # ...


.. admonition:: DEPRECATING ``@async_run_until_complete`` decorator

    * BETTER: Use nornmal step decorators instead.
    * The support for ``@async_run_until_complete`` decorator will be removed in behave v1.4.0.

.. seealso::

    * :this_repo:`features/step.async_steps.feature`


Changes
-------------------------------------------------------------------------------

:class:`~behave.runner.ModelRunner`:

* Simplify signature on method ``run_hook(context, *args)`` to ``run_hook(*args)``

NEW :mod:`behave.model_type` module:

* Moved generic model classes here from :mod:`behave.model_core` module, like:
  :class:`behave.model_core.Status`, :class:`behave.model_core.FileLocation`.


.. include:: _common_extlinks.rst
