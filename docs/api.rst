.. _api:

====================
Behave API Reference
====================

This reference is meant for people actually writing step implementations
for feature tests. It contains way more information than a typical step
implementation will need: most implementations will only need to look at
the basic implementation of `step functions`_ and *maybe*
`environment file functions`_.

The model stuff is for people getting really *serious* about their step
implementations.

.. note::

   Anywhere this document says "string" it means "unicode string" in
   Python 2.x

   *behave* works exclusively with unicode strings internally.


Step Functions
==============

Step functions are implemented in the Python modules present in your
"steps" directory. All Python files (files ending in ".py") in that
directory will be imported to find step implementations. They are all
loaded before *behave* starts executing your feature tests.

Step functions are identified using step decorators. All step
implementations **should normally** start with the import line:

.. code-block:: python

    from behave import *

This line imports several decorators defined by *behave* to allow you to
identify your step functions. These are available in both PEP-8 (all
lowercase) and traditional (title case) versions: "given", "when", "then"
and the generic "step". See the `full list of variables imported`_ in the
above statement.

.. _`full list of variables imported`: #from-behave-import-*

The decorators all take a single string argument: the string to match
against the feature file step text *exactly*. So the following step
implementation code:

.. code-block:: python

    @given(u'some known state')
    def step_impl(context):
        setup_something(some, state)


will match the "Given" step from the following feature:

.. code-block:: gherkin

    Scenario: test something
      Given some known state
      Then  some observed outcome.

*You don't need to import the decorators*: they're automatically available
to your step implementation modules as `global variables`_.

.. _`global variables`: #step-global-variables

Steps beginning with "and" or "but" in the feature file are renamed to take
the name of their preceding keyword, so given the following feature file:

.. code-block:: gherkin

    Given some known state
      And some other known state
     When some action is taken
     Then some outcome is observed
      But some other outcome is not observed.

the first "and" step will be renamed internally to "given" and *behave*
will look for a step implementation decorated with either "given" or "step":

.. code-block:: python

    @given(u'some other known state')
    def step_impl(context):
        setup_something(some, other, state)

and similarly the "but" would be renamed internally to "then". Multiple
"and" or "but" steps in a row would inherit the non-"and" or "but" keyword.

The function decorated by the step decorator will be passed at least one
argument. The first argument is always the :class:`~behave.runner.Context`
variable. Additional arguments come from `step parameters`_, if any.


Step Parameters
---------------

You may additionally use :ref:`parameters <docid.tutorial.step-parameters>` in your step names. These will be
handled by either the default simple parser (:pypi:`parse`),
its extension "cfparse" or by regular expressions
if you invoke :func:`~behave.use_step_matcher`.


.. autofunction:: behave.use_step_matcher

You may add new types to the default parser by invoking
:func:`~behave.register_type`.

.. autofunction:: behave.register_type

.. hidden:

    # -- SUPERCEEDED BY: behave.register_type documentation
    An example of this in action could be, in steps.py:

    .. code-block:: python

        from behave import register_type
        def convert_string_to_upper_case(text):
            return text.upper
        register_type(ToUpperCase=convert_string_to_upper_case)

        @given(u'a string {param:ToUpperCase} a custom type')
        def step_impl(context, param):
            assert param.isupper()


You may define a new parameter matcher by subclassing
:class:`behave.matchers.Matcher` and registering it with
:attr:`behave.matchers.matcher_mapping` which is a dictionary of "matcher
name" to :class:`~behave.matchers.Matcher` class.

.. autoclass:: behave.matchers.Matcher
   :members:

.. autoclass:: behave.model_core.Argument

.. autoclass:: behave.matchers.Match


.. _docid.api.execute-steps:
.. _docid.api.calling-steps-from-other-steps:

Step Macro: Calling Steps From Other Steps
------------------------------------------

If you find you'd like your step implementation to invoke another step you
may do so with the :class:`~behave.runner.Context` method
:func:`~behave.runner.Context.execute_steps`.

This function allows you to, for example:

.. code-block:: python

    @when(u'I do the same thing as before with the {color:w} button')
    def step_impl(context, color):
        context.execute_steps(u'''
            When I press the big {color} button
             And I duck
        '''.format(color=color))

This will cause the "when I do the same thing as before with the red button" step
to execute the other two steps as though they had also appeared in the scenario file.


from behave import *
--------------------

The import statement:

.. code-block:: python

    from behave import *

is written to introduce a restricted set of variables into your code:

=========================== =========== ===========================================
Name                        Kind        Description
=========================== =========== ===========================================
given, when, then, step     Decorator   Decorators for step implementations.
use_step_matcher(name)      Function    Selects current step matcher (parser).
register_type(Type=func)    Function    Registers a type converter.
=========================== =========== ===========================================

See also the description in `step parameters`_.



Environment File Functions
==========================

The environment.py module may define code to run before and after certain
events during your testing:

**before_all(context), after_all(context)**
  These run before and after the whole shooting match.

**before_feature(context, feature), after_feature(context, feature)**
  These run before and after each feature is executed.
  The feature object, that is passed in, is an instance of :class:`~behave.model.Feature`.

**before_rule(context, rule), after_rule(context, rule)**
  These run before and after each rule is execured.
  The rule object, that is passed in, is an instance of :class:`~behave.model.Rule`.

**before_scenario(context, scenario), after_scenario(context, scenario)**
  These run before and after each scenario is run.
  The scenario object, that is passed in, is an instance of :class:`~behave.model.Scenario`.

**before_step(context, step), after_step(context, step)**
  These run before and after every step.
  The step object, that is passed in, is an instance of :class:`~behave.model.Step`.

**before_tag(context, tag), after_tag(context, tag)**
  These run before and after a section tagged with the given name. They are
  invoked for each tag encountered in the order they're found in the
  feature file. See  :ref:`controlling things with tags`.

  Taggable statements are: Feature, Rule, Scenario, ScenarioOutline, Examples.

  The tag, that is passed in, is an instance of :class:`~behave.model.Tag` and
  because it's a subclass of string you can do simple tests like:

  .. code-block:: python

      # -- ASSUMING: tags @browser.chrome or @browser.any are used.
      # BETTER: Use Fixture for this example.
      def before_tag(context, tag):
          if tag.startswith("browser."):
              browser_type = tag.replace("browser.", "", 1)
              if browser_type == "chrome":
                  context.browser = webdriver.Chrome()
              else:
                  context.browser = webdriver.PlainVanilla()



Some Useful Environment Ideas
-----------------------------

Here's some ideas for things you could use the environment for.

Logging Setup
~~~~~~~~~~~~~~

The following recipe works in all cases (log-capture on or off).
If you want to use/configure logging, you should use the following snippet:

.. code-block:: python

    # -- FILE:features/environment.py
    def before_all(context):
        # -- SET LOG LEVEL: behave --logging-level=ERROR ...
        # on behave command-line or in "behave.ini".
        context.config.setup_logging()

        # -- ALTERNATIVE: Setup logging with a configuration file.
        # context.config.setup_logging(configfile="behave_logging.ini")


Capture Logging in Hooks
~~~~~~~~~~~~~~~~~~~~~~~~

If you wish to capture any logging generated during an environment
hook function's invocation, you may use the
:func:`~behave.log_capture.capture` decorator, like:

.. code-block:: python

    # -- FILE:features/environment.py
    from behave.log_capture import capture

    @capture
    def after_scenario(context):
        ...

This will capture any logging done during the call to *after_scenario*
and print it out.


Detecting that user code overwrites behave Context attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The *context* variable in all cases is an instance of
:class:`behave.runner.Context`.

.. autoclass:: behave.runner.Context
   :members:

.. autoclass:: behave.runner.ContextMaskWarning


Fixtures
================

.. excluded:

    .. automodule:: behave.fixture

Provide a Fixture
------------------

.. autofunction:: behave.fixture.fixture

Use Fixtures
------------------

.. autofunction:: behave.fixture.use_fixture

.. autofunction:: behave.fixture.use_fixture_by_tag

.. autofunction:: behave.fixture.use_composite_fixture_with


Runner Operation
================

The execution of code is based on the Gherkin description in `*.feature` files.
The following section provides a short overview of the hierarchical containment
that is possible in the Gherkin grammer:

.. parsed-literal::

    # -- SIMPLIFIED GHERKIN GRAMMAR (for Gherkin v6):
    # CARDINALITY DECORATOR: '*' means 0..N (many), '?' means 0..1 (optional)
    # EXAMPLE: Feature
    #   A Feature can have many Tags (as TaggableStatement: zero or more tags before its keyword).
    #   A Feature can have an optional Background.
    #   A Feature can have many Scenario(s), meaning zero or more Scenarios.
    #   A Feature can have many ScenarioOutline(s).
    #   A Feature can have many Rule(s).
    Feature(TaggableStatement):
        Background?
        Scenario*
        ScenarioOutline*
        Rule*

    Background:
        Step*           # Background steps are injected into any Scenario of its scope.

    Scenario(TaggableStatement):
        Step*

    ScenarioOutline(ScenarioTemplateWithPlaceholders):
        Scenario*       # Rendered Template by using ScenarioOutline.Examples.rows placeholder values.

    Rule(TaggableStatement):
        Background?     # Behave-specific extension (after removal from final Gherkin v6).
        Scenario*
        ScenarioOutline*


Given all the code that could be run by *behave*,
this is the order in which that code is invoked (if they exist.)

.. parsed-literal::

    # -- PSEUDO-CODE:
    # HOOK: before_tag(), after_tag() is called for Feature, Rule, Scenario
    ctx = createContext()
    call-optional-hook before_all(ctx)
    for feature in all_features:
        for tag in feature.tags: call-optional-hook before_tag(ctx, tag)
        call-optional-hook before_feature(ctx, feature)
        for run_item in feature.run_items:  # CAN BE: Rule, Scenario, ScenarioOutline
            execute_run_item(run_item, ctx)
        call-optional-hook after_feature(ctx, feature)
        for tag in feature.tags: call-optional-hook after_tag(ctx, tag)
    call-optional-hook after_all(ctx)

    function execute_run_item(run_item, ctx):
        if run_item isa Rule:
            # -- CASE: Rule
            rule = run_item
            for tag in rule.tags: call-optional-hook before_tag(ctx, tag)
            call-optional-hook before_rule(ctx, rule)
            for run_item in rule.run_items:     # CAN BE: Scenario, ScenarioOutline
                execute_run_item(run_item, ctx)
            call-optional-hook after_rule(ctx, rule)
            for tag in rule.tags: call-optional-hook after_tag(ctx, tag)
        else if run_item isa ScenarioOutline:
            # -- CASE: ScenarioOutline
            # HINT: All Scenarios are already created from Example(s) rows.
            scenario_outline = run_item
            for scenario in scenario_outline.scenarios:
                execute_run_item(scenario, ctx)
        else if run_item isa Scenario:
            # -- CASE: Scenario
            # HINT: Background steps are injected before scenario steps.
            scenario = run_item
            for tag in scenario.tags: call-optional-hook before_tag(ctx, tag)
            call-optional-hook before_scenario(ctx, scenario)
            for step in scenario.steps:
                call-optional-hook before_step(ctx, step)
                step.run(ctx)
                call-optional-hook after_step(ctx, step)
            call-optional-hook after_scenario(ctx, scenario)
            for tag in scenario.tags: call-optional-hook after_tag(ctx, tag)


Model Objects
=============

The feature, scenario and step objects represent the information parsed
from the feature file. They have a number of common attributes:

**keyword**
    "Feature", "Scenario", "Given", etc.

**name**
    The name of the step (the text after the keyword.)

**filename** and **line**
    The file name (or "<string>") and line number of the statement.

The structure of model objects parsed from a *feature file* will typically
be:

.. parsed-literal::

    :class:`~behave.model.Tag` (as :py:attr:`Feature.tags`)
    :class:`~behave.model.Feature` : TaggableModelElement
        Description (as :py:attr:`Feature.description`)

        :class:`~behave.model.Background`
            :class:`~behave.model.Step`
                :class:`~behave.model.Table` (as :py:attr:`Step.table`)
                MultiLineText (as :py:attr:`Step.text`)

        :class:`~behave.model.Tag` (as :py:attr:`Scenario.tags`)
        :class:`~behave.model.Scenario` : TaggableModelElement
            Description (as :py:attr:`Scenario.description`)
            :class:`~behave.model.Step`
                :class:`~behave.model.Table` (as :py:attr:`Step.table`)
                MultiLineText (as :py:attr:`Step.text`)

        :class:`~behave.model.Tag` (as :py:attr:`ScenarioOutline.tags`)
        :class:`~behave.model.ScenarioOutline` : TaggableModelElement
            Description (as :py:attr:`ScenarioOutline.description`)
            :class:`~behave.model.Step`
                :class:`~behave.model.Table` (as :py:attr:`Step.table`)
                MultiLineText (as :py:attr:`Step.text`)
            :class:`~behave.model.Examples`
                :class:`~behave.model.Table`


.. autoclass:: behave.model.Feature

.. autoclass:: behave.model.Rule

.. autoclass:: behave.model.Background

.. autoclass:: behave.model.Scenario

.. autoclass:: behave.model.ScenarioOutline

.. autoclass:: behave.model.Examples

.. autoclass:: behave.model.Tag

.. autoclass:: behave.model.Step

Tables may be associated with either Examples or Steps:

.. autoclass:: behave.model.Table

.. autoclass:: behave.model.Row

And Text may be associated with Steps:

.. autoclass:: behave.model.Text



Logging Capture
===============

The logging capture *behave* uses by default is implemented by the class
:class:`~behave.log_capture.LoggingCapture`. It has methods

.. autoclass:: behave.log_capture.LoggingCapture
   :members:

The *log_capture* module also defines a handy logging capture decorator that's
intended to be used on your `environment file functions`_.

.. autofunction:: behave.log_capture.capture


.. include:: _common_extlinks.rst
