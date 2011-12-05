====================
behave API reference
====================

.. if you change any headings in here make sure you haven't broken the
   cross-references in the API documentation or module docstrings!

This reference is meant for people actually writing step implementations
for feature tests. It contains way more information than a typical step
implementation will need: most implementations will only need to look at
the basic implementation of `step functions`_ and *maybe* `environment file
functions`_.

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
implementations **must** start with the import line:

.. code-block:: python

   from behave import *

Several decorators are defined by *behave* to allow you to identify your
step functions. These are available in both PEP-8 (all lowercase) and
traditional (title case) versions: "given", "when", "then" and the generic
"step". See the `full list of variables imported`_ in the above statement.

.. _`full list of variables imported`: #from-behave-import-*

The decorators all take a single string argument: the string to match
against the feature file step text *exactly*. So the following step
implementation code:

.. code-block:: python

   @given('some known state')
   def step(context):
       set_up(some, state)


will match the "Given" step from the following feature:

.. code-block:: gherkin

 Scenario: test something
  Given some known state
   then some observed outcome.

*You don't need to import the decorators*: they're automatically available
to your step implmentation modules as `global variables`_.

.. _`global variables`: #step-global-variables

Steps beginning with "and" or "but" in the feature file are renamed to take
the name of their preceding keyword, so given the following feature file:

.. code-block:: gherkin

  Given some known state
    and some other known state
   when some action is taken
   then some outcome is observed
    but some other outcome is not observed.

the first "and" step will be renamed internally to "given" and *behave*
will look for a step implementation decorated with either "given" or "step":

.. code-block:: python

  @given('some other known state')
  def step(context):
     set_up(some, other, state)
      
and similarly the "but" would be renamed internally to "then". Multiple
"and" or "but" steps in a row would inherit the non-"and" or "but" keyword.

The function decorated by the step decorator will be passed at least one
argument. The first argument is always the :class:`~behave.runner.Context`
variable. Additional arguments come from `step parameters`_, if any.


Step Parameters
---------------

You may additionally use `parameters`_ in your step names. These will be
handled by either the default `simple parser`_ or by regular expressions if
you invoke :func:`~behave.matchers.step_matcher`.

.. _`parameters`: tutorial.html#step-parameters
.. _`simple parser`: http://pypi.python.org/pypi/parse

.. autofunction:: behave.matchers.step_matcher

You may define a new parameter matcher by subclassing
:class:`behave.matchers.Matcher` and registering it with
:attr:`behave.matchers.matcher_mapping` which is a dictionary of "matcher
name" to :class:`~behave.matchers.Matcher` class.

.. autoclass:: behave.matchers.Matcher
   :members:

.. autoclass:: behave.model.Argument

.. autoclass:: behave.model.Match


Calling Steps From Other Steps
------------------------------

If you find you'd like your step implementation to invoke another step you
may do so with the context function :func:`execute_steps`.


from behave import *
--------------------

The import statement:

.. code-block:: python

  from behave import *

is written to introduce a restricted set of variables into your code:

**given**, **when**, **then**, **step**
  These are the decorators used to identify implementations.

**Given**, **When**, **Then**, **Step**
  See above.

**stop_matcher**
  This is described in `step parameters`_.


Environment File Functions
==========================

The environment.py module may define code to run before and after certain
events during your testing:

**before_step(context, step), after_step(context, step)**
  These run before and after every step. The step passed in is an instance
  of :class:`~behave.model.Step`.

**before_scenario(context, scenario), after_scenario(context, scenario)**
  These run before and after each scenario is run. The scenario passed in is an
  instance of :class:`~behave.model.Scenario`.

**before_feature(context, feature), after_feature(context, feature)**
  These run before and after each feature file is exercised. The feature
  passed in is an instance of :class:`~behave.model.Feature`.

**before_tag(context, tag), after_tag(context, tag)**
  These run before and after a section tagged with the given name. They are
  invoked for each tag encountered in the order they're found in the
  feature file. See  `controlling things with tags`_. The tag passed in is
  an instance of :class:`~behave.model.Tag` and because it's a subclass of
  string you can do simple tests like:

  .. code-block:: python

     if tag == 'browser':
         context.browser = webdriver.Chrome()

**before_all(context), after_all(context)**
  These run before and after the whole shooting match.

The *context* variable in all cases is an instance of
:class:`behave.runner.Context`.

.. autoclass:: behave.runner.Context
   :members:

.. autoclass:: behave.runner.ContextMaskWarning


Runner Operation
================

Given all the code that could be run by *behave*, this is the order in
which that code is invoked (if they exist.)

.. parsed-literal::

    before_all
    for feature in all_features:
        before_feature
        for scenario in feature.scenarios:
            before_scenario
            for step in scenario.steps:
                before_step
                    step.run()
                after_step
            after_scenario
        after_feature         
    after_all
  
If the feature contains scenario outlines then there is an addtional loop
over all the scenarios in the outline making the running look like this:

.. parsed-literal::

    before_all
    for feature in all_features:
        before_feature
        for outline in feature.scenarios:
            for scenario in outline.scenarios:
                before_scenario
                for step in scenario.steps:
                    before_step
                        step.run()
                    after_step
                after_scenario
        after_feature         
    after_all


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

    :class:`~behave.model.Feature` 
        :class:`~behave.model.Tag` 
        :class:`~behave.model.Background` 
        :class:`~behave.model.Scenario` 
           :class:`~behave.model.Tag` 
           :class:`~behave.model.Step` 
              :class:`~behave.model.Table` 
        :class:`~behave.model.ScenarioOutline` 
           :class:`~behave.model.Tag` 
           :class:`~behave.model.Examples` 
              :class:`~behave.model.Table` 
           :class:`~behave.model.Step` 
              :class:`~behave.model.Table` 

.. autoclass:: behave.model.Feature

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

.. _`controlling things with tags`: tutorial.html#controlling-things-with-tags

