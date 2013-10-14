========
Tutorial
========

.. if you change any headings in here make sure you haven't broken the
   cross-references in the API documentation or module docstrings!

First, `install *behave*.`_

.. _`Install *behave*.`: install.html

Now make a directory called "tutorial". In that directory create a file
called "tutorial.feature" containing:

.. code-block:: gherkin

 Feature: showing off behave

   Scenario: run a simple test
      Given we have behave installed
       when we implement a test
       then behave will test it for us!

Make a new directory called "tutorial/steps". In that directory create a
file called "tutorial.py" containing:

.. code-block:: python

  from behave import *

  @given('we have behave installed')
  def step_impl(context):
      pass

  @when('we implement a test')
  def step_impl(context):
      assert True is not False

  @then('behave will test it for us!')
  def step_impl(context):
      assert context.failed is False

Run behave::

    % behave
    Feature: showing off behave # tutorial/tutorial.feature:1

      Scenario: run a simple test        # tutorial/tutorial.feature:3
        Given we have behave installed   # tutorial/steps/tutorial.py:3
        When we implement a test         # tutorial/steps/tutorial.py:7
        Then behave will test it for us! # tutorial/steps/tutorial.py:11

    1 feature passed, 0 failed, 0 skipped
    1 scenario passed, 0 failed, 0 skipped
    3 steps passed, 0 failed, 0 skipped, 0 undefined

Now, continue reading to learn how to make the most of *behave*.


Features
========

*behave* operates on directories containing:

1. `feature files`_ written by your Business Analyst / Sponsor / whoever
   with your behaviour scenarios in it, and
2. a "steps" directory with `Python step implementations`_ for the
   scenarios.

You may optionally include some `environmental controls`_ (code to run
before and after steps, scenarios, features or the whole shooting
match).

The minimum requirement for a features directory is::

  features/
  features/everything.feature
  features/steps/
  features/steps/steps.py

A more complex directory might look like::

  features/
  features/signup.feature
  features/login.feature
  features/account_details.feature
  features/environment.py
  features/steps/
  features/steps/website.py
  features/steps/utils.py

If you're having trouble setting things up and want to see what *behave* is
doing in attempting to find your features use the "-v" (verbose)
command-line switch.


Feature Files
=============

A feature file has a `natural language format`_ describing a feature or
part of a feature with representative examples of expected outcomes.
They're plain-text (encoded in UTF-8) and look something like:

.. _`natural language format`: gherkin.html#gherkin:-feature-testing-language

.. code-block:: gherkin

  Feature: Fight or flight
    In order to increase the ninja survival rate,
    As a ninja commander
    I want my ninjas to decide whether to take on an 
    opponent based on their skill levels

    Scenario: Weaker opponent
      Given the ninja has a third level black-belt 
       When attacked by a samurai
       Then the ninja should engage the opponent

    Scenario: Stronger opponent
      Given the ninja has a third level black-belt 
       When attacked by Chuck Norris
       Then the ninja should run for his life

The "Given", "When" and "Then" parts of this prose form the actual steps
that will be taken by *behave* in testing your system. These map to `Python
step implementations`_. As a general guide:

**Given** we *put the system in a known state* before the
user (or external system) starts interacting with the system (in the When
steps). Avoid talking about user interaction in givens.

**When** we *take key actions* the user (or external system) performs. This
is the interaction with your system which should (or perhaps should not)
cause some state to change.

**Then** we *observe outcomes*.

You may also include "And" or "But" as a step - these are renamed by *behave*
to take the name of their preceding step, so:

.. code-block:: gherkin

    Scenario: Stronger opponent
      Given the ninja has a third level black-belt 
       When attacked by Chuck Norris
       Then the ninja should run for his life
        And fall off a cliff

In this case *behave* will look for a step definiton for "Then fall off a
cliff".


Scenario Outlines
-----------------

Sometimes a scenario should be run with a number of variables giving a set
of known states, actions to take and expected outcomes, all using the same
basic actions. You may use a Scenario Outline to achieve this:

.. code-block:: gherkin

  Scenario Outline: Blenders
     Given I put <thing> in a blender,
      when I switch the blender on
      then it should transform into <other thing>

   Examples: Amphibians
     | thing         | other thing |
     | Red Tree Frog | mush        |

   Examples: Consumer Electronics
     | thing         | other thing |
     | iPhone        | toxic waste |
     | Galaxy Nexus  | toxic waste |

*behave* will run the scenario once for each (non-heading) line appearing
in the example data tables.


Step Data
---------

Sometimes it's useful to associate a table of data with your step.

Any text block following a step wrapped in ``"""`` lines will be associated
with the step. For example:

.. code-block:: gherkin

   Scenario: some scenario
     Given a sample text loaded into the frobulator
        """
        Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do
        eiusmod tempor incididunt ut labore et dolore magna aliqua.
        """
    When we activate the frobulator
    Then we will find it similar to English

The text is available to the Python step code as the ".text" attribute
in the :class:`~behave.runner.Context` variable passed into each step
function.

You may also associate a table of data with a step by simply entering it,
indented, following the step. This can be useful for loading specific
required data into a model.

.. code-block:: gherkin

   Scenario: some scenario
     Given a set of specific users
        | name      | department  |
        | Barry     | Beer Cans   |
        | Pudey     | Silly Walks |
        | Two-Lumps | Silly Walks | 
 
    When we count the number of people in each department
    Then we will find two people in "Silly Walks"
     But we will find one person in "Beer Cans"

The table is available to the Python step code as the ".table" attribute
in the :class:`~behave.runner.Context` variable passed into each step
function. The table for the example above could be accessed like so:

.. code-block:: python

  @given('a set of specific users')
  def step_impl(context):
      for row in context.table:
          model.add_user(name=row['name'], department=row['department'])

There's a variety of ways to access the table data - see the
:class:`~behave.model.Table` API documentation for the full details.



Python Step Implementations
===========================

Steps used in the scenarios are implemented in Python files in the "steps"
directory. You can call these whatever you like as long as they're
*filename*.py in the steps directory. You don't need to tell *behave* which
ones to use - it'll use all of them.

The full detail of the Python side of *behave* is in the `API
documenation`_.

.. _`API documenation`: api.html

Steps are identified using decorators which match the predicate from the
feature file: given, when, then and step (variants with Title case are also
available if that's your preference.) The decorator accepts a string
containing the rest of the phrase used in the scenario step it belongs to.

Given a Scenario:

.. code-block:: gherkin

  Scenario: Search for an account
     Given I search for a valid account
      Then I will see the account details

Step code implementing the two steps here might look like (using selenium
webdriver and some other helpers):

.. code-block:: python

 @given('I search for a valid account')
 def step_impl(context):
    context.browser.get('http://localhost:8000/index')
    form = get_element(context.browser, tag='form')
    get_element(form, name="msisdn").send_keys('61415551234')
    form.submit()

 @then('I will see the account details')
 def step_impl(context):
    elements = find_elements(context.browser, id='no-account')
    eq_(elements, [], 'account not found')
    h = get_element(context.browser, id='account-head')
    ok_(h.text.startswith("Account 61415551234"),
        'Heading %r has wrong text' % h.text)

The ``step`` decorator matches the step to *any* step type, "given", "when"
or "then". The "and" and "but" step types are renamed internally to take
the preceding step's keyword (so an "and" following a "given" will become a
"given" internally and use a "give" decorated step).

If you find you'd like your step implementation to invoke another step you
may do so with the :class:`~behave.runner.Context` method
:func:`~behave.runner.Context.execute_steps`.

This function allows you to, for example:

.. code-block:: python

    @when('I do the same thing as before')
    def step_impl(context):
        context.execute_steps('''
            when I press the big red button
             and I duck
        ''')

This will cause the "when I do the same thing as before" step to execute
the other two steps as though they had also appeared in the scenario file.


Step Parameters
---------------

You may find that your feature steps sometimes include very common phrases
with only some variation. For example:

.. code-block:: gherkin

  Scenario: look up a book
    Given I search for a valid book
     Then the result page will include "success"

  Scenario: look up an invalid book
    Given I search for a invalid book
     Then the result page will include "failure"

You may define a single Python step that handles both of those Then
clauses (with a Given step that puts some text into
``context.response``):

.. code-block:: python

 @then('the result page will include "{text}"')
 def step_impl(context, text):
    if text not in context.response:
        fail('%r not in %r' % (message, context.response))

There's two parsers available by default in *behave*:

**parse** (the default)
  This is a `simple parser`_ that uses a format very much like the Python
  builtin ``format()``. You must use named fields which are then matched to
  your ``step()`` function arguments.
**re**
  This uses full regular expressions to parse the clause text. You will
  need to use named groups "(?P<name>...)" to define the variables pulled
  from the text and passed to your ``step()`` function.

To specify which parser to use invoke :func:`~behave.matchers.step_matcher`
with the name of the matcher to use. You may change matcher to suit
specific step functions - the last call to ``step_matcher`` before a step
function declaration will be the one it uses.

.. _`simple parser`: http://pypi.python.org/pypi/parse

Context
-------

You'll have noticed the "context" variable that's passed around. It's a
clever place where you and *behave* can store information to share around.
It runs at three levels, automatically managed by *behave*. 

When *behave* launches into a new feature or scenario it adds a new layer
to the context, allowing the new activity level to add new values, or
overwrite ones previosuly defined, for the duration of that activity. These
can be thought of as scopes.

You can define values in your `environmental controls`_ file which may be
set at the feature level and then overridden for some scenarios. Changes
made at the scenario level won't permanently affect the value set at the
feature level.

You may also use it to share values between steps. For example, in some
steps you define you might have:

.. code-block:: python

  @given('I request a new widget for an account via SOAP')
  def step_impl(context):
      client = Client("http://127.0.0.1:8000/soap/")
      context.response = client.Allocate(customer_first='Firstname',
          customer_last='Lastname', colour='red')

  @then('I should receive an OK SOAP response')
  def step_impl(context):
      eq_(context.response['ok'], 1)

There's also some values added to the context by *behave* itself:

**table**
  This holds any table data associated with a step.

**text**
  This holds any multiline text associated with a step.

**failed**
  This is set at the root of the context when any step fails. It is
  sometimes useful to use this combined with the ``--stop`` command-line
  option to prevent some mis-behaving resource from being cleaned up in an
  ``after_feature()`` or similar (for example, a web browser being driven
  by Selenium.)

The *context* variable in all cases is an instance of
:class:`behave.runner.Context`.


Environmental Controls
======================

The environment.py module may define code to run before and after certain
events during your testing:

**before_step(context, step), after_step(context, step)**
  These run before and after every step.
**before_scenario(context, scenario), after_scenario(context, scenario)**
  These run before and after each scenario is run.
**before_feature(context, feature), after_feature(context, feature)**
  These run before and after each feature file is exercised.
**before_tag(context, tag), after_tag(context, tag)**
  These run before and after a section tagged with the given name. They are
  invoked for each tag encountered in the order they're found in the
  feature file. See  `controlling things with tags`_.
**before_all(context), after_all(context)**
  These run before and after the whole shooting match.

The feature, scenario and step objects represent the information parsed
from the feature file. They have a number of attributes:

**keyword**
  "Feature", "Scenario", "Given", etc.
**name**
  The name of the step (the text after the keyword.)
**tags**
  A list of the tags attached to the section or step. See `controlling
  things with tags`_.
**filename** and **line**
  The file name (or "<string>") and line number of the statement.

A common use-case for environmental controls might be to set up a web
server and browser to run all your tests in. For example:

.. code-block:: python

  import threading
  from wsgiref import simple_server
  from selenium import webdriver
  from my_application import model
  from my_application import web_app

  def before_all(context):
      context.server = simple_server.WSGIServer(('', 8000))
      context.server.set_app(web_app.main(environment='test'))
      context.thread = threading.Thread(target=context.server.serve_forever)
      context.thread.start()
      context.browser = webdriver.Chrome()

  def after_all(context):
      context.server.shutdown()
      context.thread.join()
      context.browser.quit()

  def before_feature(context, feature):
      model.init(environment='test')

Of course if you wish you could have a new browser for each feature, or to
retain the database state between features or even initialise the database
for to each scenario.


Controlling Things With Tags
============================

You may also "tag" parts of your feature file. At the simplest level this
allows *behave* to selectively check parts of your feature set.

Given a feature file with:

.. code-block:: gherkin

  Feature: Fight or flight
    In order to increase the ninja survival rate,
    As a ninja commander
    I want my ninjas to decide whether to take on an 
    opponent based on their skill levels

    @slow
    Scenario: Weaker opponent
      Given the ninja has a third level black-belt 
      When attacked by a samurai
      Then the ninja should engage the opponent

    Scenario: Stronger opponent
      Given the ninja has a third level black-belt 
      When attacked by Chuck Norris
      Then the ninja should run for his life
      
then running ``behave --tags=slow`` will run just the scenarios tagged
``@slow``. If you wish to check everything *except* the slow ones then you
may run ``behave --tags=-slow``.

Another common use-case is to tag a scenario you're working on with
``@wip`` and then ``behave --tags=wip`` to just test that one case.

Tag selection on the command-line may be combined:

**--tags=wip,slow**
   This will select all the cases tagged *either* "wip" or "slow".

**--tags=wip --tags=slow**
   This will select all the cases tagged *both* "wip" and "slow".

If a feature or scenario is tagged and then skipped because of a
command-line control then the *before_* and *after_* environment functions
will not be called for that feature or scenario. Note that *behave* has
additional support specifically for testing `works in progress`_.

The tags attached to a feature and scenario are available in
the environment functions via the "feature" or "scenario" object passed to
them. On those objects there is an attribute called "tags" which is a list
of the tag names attached, in the order they're found in the features file.

There are also `environmental controls`_ specific to tags, so in the above
example *behave* will attempt to invoke an ``environment.py`` function
``before_tag`` and ``after_tag`` before and after the Scenario tagged
``@slow``, passing in the name "slow". If multiple tags are present then
the functions will be called multiple times with each tag in the order
they're defined in the feature file.

Re-visiting the example from above; if only some of the features required a
browser and web server then you could tag them ``@browser``:

.. code-block:: python

  def before_feature(context, feature):
      model.init(environment='test')
      if 'browser' in feature.tags:
          context.server = simple_server.WSGIServer(('', 8000))
          context.server.set_app(web_app.main(environment='test'))
          context.thread = threading.Thread(target=context.server.serve_forever)
          context.thread.start()
          context.browser = webdriver.Chrome()

  def after_feature(context, feature):
      if 'browser' in feature.tags:
          context.server.shutdown()
          context.thread.join()
          context.browser.quit()

Works In Progress
=================

*behave* supports the concept of a highly-unstable "work in progress"
scenario that you're actively developing. This scenario may produce strange
logging, or odd output to stdout or just plain interact in unexepected ways
with *behave*'s scenario runner.

To make testing such scenarios simpler we've implemented a "-w"
command-line flag. This flag:

1. turns off stdout capture
2. turns off logging capture; you will still need to configure your own
   logging handlers - we recommend a ``before_all()`` with:

   .. code-block:: python

    if not context.config.log_capture:
        logging.basicConfig(level=logging.DEBUG)
     
3. turns off pretty output - no ANSI escape sequences to confuse your
   scenario's output
4. only runs scenarios tagged with "@wip"
5. stops at the first error

