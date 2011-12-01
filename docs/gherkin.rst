=====================
Feature Testing Setup
=====================

.. if you change any headings in here make sure you haven't broken the
   cross-references in the API documentation or module docstrings!

Feature Testing Layout
======================

The simplest way to make *behave* work is to create a directory called
"features" containing:

1. feature files written by your Business Analyst / Sponsor / whoever
   with your behaviour scenarios in it, and
2. a "steps" directory with `Python step implementations`_ for the
   scenarios.

You may optionally include some `environmental controls`_ (code to run
before and after steps, scenarios, features or the whole shooting
match).

.. _`Python step implementations`: tutorial.html#python-step-implementations
.. _`environmental controls`: tutorial.html#environmental-controls

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


Layout Variations
-----------------

*behave* has some flexibility built in. It will actually try quite hard to
find feature specifications. When launched you may pass on the command
line:

**a features directory path**
  This is the path to a features directory laid out as described above. It may be called
  anything by *must* contain at least one "*name*.feature" file and a directory
  called "steps". The "environment.py" file, if present, must be in the same
  directory that contains the "steps" directory (not *in* the "steps"
  directory).

**the path to a "*name*.feature" file**
  This tells *behave* where to find the feature file. To find the steps
  directory *behave* will look in the directory containing the feature
  file. If it is not present, *behave* will look in the parent directory,
  and then its parent, and so on until it hits the root of the filesystem.
  The "environment.py" file, if present, must be in the same directory
  that contains the "steps" directory (not *in* the "steps" directory).

**a directory containing your feature files**
  Similar to the approach above, you're identifying the directory where your
  "*name*.feature" files are, and if the "steps" directory is not in the
  same place then *behave* will search for it just like above. This allows
  you to have a layout like::

   tests/
   tests/environment.py
   tests/features/signup.feature
   tests/features/login.feature
   tests/features/account_details.feature
   tests/steps/
   tests/steps/website.py
   tests/steps/utils.py

If you're having trouble setting things up and want to see what *behave* is
doing in attempting to find your features use the "-v" (verbose)
command-line switch.


Gherkin: Feature Testing Language
=================================

*behave* uses a language called `Gherkin`_ (with with `some
modifications`_) to structure the feature files.

.. _`some modifications`: #modifications-to-the-gherkin-standard

These files should be written using natural language - ideally by the
non-technical business participants in the software project. Feature files
serve two purposes – documentation and automated tests.

It is very flexible but has a few simple rules that writers need to adhere to.

Feature files contain a single `feature`_ and are named "*name*.feature".

.. _`feature`: #features

Line endings terminate statements (eg, steps). Either spaces or tabs may be
used for indentation (but spaces are more portable). Indentation is almost
always ignored - it's a tool for the feature writer to express some
structure in the text. Most lines start with a keyword.

Comment lines are allowed anywhere in the file. They begin with zero or
more spaces, followed by a sharp sign (#) and some amount of text.

.. _`gherkin`: https://github.com/cucumber/cucumber/wiki/Gherkin


Features
--------

Features are composed of scenarios. They may optionally have a description,
a background and a set of tags. In its simplest form a feature looks like:

.. code-block:: gherkin

  Feature: feature name

    Scenario: some scenario
        Given some condition
         Then some result is expected.

In all its glory it could look like:

.. code-block:: gherkin

  @tags @tag
  Feature: feature name
    description
    further description

    Background: some requirement of this test
      Given some setup condition
        And some other setup action

    Scenario: some scenario
        Given some condition
         When some action is taken
         Then some result is expected.

    Scenario: some other scenario
        Given some other condition
         When some action is taken
         Then some other result is expected.

    Scenario: ...

The feature name should just be some reasonably descriptive title for the
feature being tested, like "the message posting interface". The following
description is optional and serves to clarify any potential confusion or
scope issue in the feature name. The description is for the benefit of
humans reading the feature text.

.. any other advice we could include here?

The Background and Scenarios will be discussed in the following sections.


Backgrounds
-----------

A background is a series of steps to be executed before the scenarios for
the feature are tested. It is run just once, and is useful for performing
setup operations like logging into a web browser or setting up a database
with test data used by the scenarios. The background description is for the
benefit of humans reading the feature text.

Again the background name should just be a reasonably descriptive title
for the background operation being performed or requirement being met.

The background is not tested for failure. If it's something that can fail
then it probably should be a scenario to be tested.

It contains `steps`_ as described below.

**Good practices for using Background**

Don’t use “Background” to set up complicated state unless that state is actually something the client needs to know.
 For example, if the user and site names don’t matter to the client, you
 should use a high-level step such as “Given that I am logged in as a site
 owner”.

Keep your “Background” section short.
 You’re expecting the user to actually remember this stuff when reading
 your scenarios. If the background is more than 4 lines long, can you move
 some of the irrelevant details into high-level steps? See Calling Steps
 from Step Definitions.

Make your “Background” section vivid.
 You should use colorful names and try to tell a story, because the human
 brain can keep track of stories much better than it can keep track of
 names like “User A”, “User B”, “Site 1”, and so on.

Keep your scenarios short, and don’t have too many.
 If the background section has scrolled off the screen, you should think
 about using higher-level steps, or splitting the features file in two.


Scenarios
---------

Scenarios describe the discrete behaviours being tested. They are given a
title which should be a reasonably descriptive title for the scenario being
tested. The scenario description is for the benefit of humans reading the
feature text.

Scenarios are composed of a series of `steps`_ as described below. The
steps typically take the form of "given some condition" "then we expect
some test will pass." In this simplest form, a scenario might be:

.. code-block:: gherkin

 Scenario: we have some stock when we open the store
   Given that the store has just opened
    then we should have items for sale.

There may be additional conditions imposed on the scenario, and these would
take the form of "when" steps following the initial "given" condition. If
necessary, additional "and" or "but" steps may also follow the "given",
"when" and "then" steps if more needs to be tested. A more complex example
of a scenario might be:

.. code-block:: gherkin

 Scenario: Replaced items should be returned to stock
   Given that a customer buys a blue garment
     and I have two blue garments in stock
     but I have no red garments in stock
     and three black garments in stock.
    When he returns the garment for a replacement in black,
    then I should have three blue garments in stock
     and no red garments in stock,
     and two black garments in stock.

It is good practise to have a scenario test only one behaviour or desired
outcome.

Scenarios contain `steps`_ as described below.


Scenario Outlines
-----------------

These may be used when you have a set of expected conditions and outcomes
to go along with your scenario `steps`_.

An outline includes keywords in the step definitons which are filled in
using values from example tables. You may have a number of example tables
in each scenario outline.

.. code-block:: gherkin

  Scenario Outline: Blenders
     When I put <thing> in a blender
     Then <other thing> should ensue

   Examples: Amphipians
     | thing         | other thing |
     | Red Tree Frog | mush        |

   Examples: Consumer Electronics
     | thing         | other thing |
     | iPhone        | toxic waste |
     | Galaxy Nexus  | toxic waste |


Steps
-----

Steps take a line each and begin with a *keyword* - one of "given", "when",
"then", "and" or "but".

In a formal sense the keywords are all Title Case, though some languages
allow all-lowercase keywords where that makes sense.

Steps should not need to contain significant degree of detail about the
mechanics of testing; that is, instead of:

.. code-block:: gherkin

  Given a browser client is used to load the URL "http://website.example/website/home.html"

the step could instead simply say:

.. code-block:: gherkin

  Given we are looking at the home page

Steps are implemented using Python code which is implemented in the "steps"
directory in Python modules (files with Python code which are named
"*name*.py".) The naming of the Python modules does not matter. *All* modules
in the "steps" directory will be imported by *behave* at startup to
discover the step implementations.

Given, When, Then, And, But
~~~~~~~~~~~~~~~~~~~~~~~~~~~

*behave* doesn't technically distinguish between the various kinds of steps.
However, we strongly recommend that you do! These words have been carefully
selected for their purpose, and you should know what the purpose is to get
into the BDD mindset.

**Given**

The purpose of givens is to **put the system in a known state** before the
user (or external system) starts interacting with the system (in the When
steps). Avoid talking about user interaction in givens.  If you had worked
with usecases, you would call this preconditions.

Examples:

- Create records (model instances) / set up the database state.
- It's ok to call directly into your application model here.
- Log in a user (An exception to the no-interaction recommendation. Things
  that "happened earlier" are ok).

You might also use Given with a multiline table argument to set up database
records instead of fixtures hard-coded in steps. This way you can read
the scenario and make sense out of it without having to look elsewhere (at
the fixtures).

**When**

The purpose of When steps is to **describe the key action** the user
performs. This is the user interaction with your system which should (or
perhaps should not) cause some state to change.

Examples:

- Interact with a web page (`Requests`_/`Twill`_/`Selenium`_ *interaction*
  etc   should mostly go into When steps).
- Interact with some other user interface element.
- Developing a library? Kicking off some kind of action that has an
  observable effect somewhere else.

.. _`requests`: http://python-requests.org/
.. _`twill`: http://twill.idyll.org/
.. _`selenium`: http://seleniumhq.org/projects/webdriver/

**Then**

The purpose of Then steps is to **observe outcomes**. The observations should
be related to the business value/benefit in your feature description. The
observations should also be on some kind of *output* - that is something
that comes *out* of the system (report, user interface, message) and not
something that is deeply buried inside it (that has no business value).

Examples:

- Verify that something related to the Given+When is (or is not) in the output
- Check that some external system has received the expected message (was an
  email with specific content sent?)

While it might be tempting to implement Then steps to just look in the
database - resist the temptation. You should only verify outcome that is
observable for the user (or external system) and databases usually are not.

**And, But**

If you have several givens, whens or thens you can write:

.. code-block:: gherkin

  Scenario: Multiple Givens
    Given one thing
    Given an other thing
    Given yet an other thing
     When I open my eyes
     Then I see something
     Then I don't see something else


Or you can make it read more fluently by writing:

.. code-block:: gherkin

  Scenario: Multiple Givens
    Given one thing
      And an other thing
      And yet an other thing
     When I open my eyes
     Then I see something
      But I don't see something else

To *behave* steps beginning with "and" or "but" are exactly the same kind
of steps as all the others.


Step Data
~~~~~~~~~

Steps may have some text or a table of data attached to them.

**text**
  Any indented text following a step which does not itself start with a
  Gherkin keyword will be associated with the step. This is the one case
  where indentation is actually parsed: the leading whitespace is stripped
  from the text, and successive lines of the text should have at least the
  same amount of whitespace as the first line.

  The step text is available to the Python step code as the ".text" attribute
  in the :class:`behave.runner.Context` variable.

**table**
  TODO


Tags
----

TODO


Languages Other Than English
----------------------------

English is the default language used in parsing feature files. If you wish
to use a different language you should check to see whether it is
available::

   behave --lang-list

This command lists all the supported languages. If yours is present then
you have two options:

1. add a line to the top of the feature files like (for French):

    # language: fr

2. use the command-line switch ``--lang``::

    behave --lang=fr

The feature file keywords will now use the French translations. To see what
the language equivalents recognised by *behave* are, use::

   behave --lang-help fr


Modifications to the Gherkin Standard
-------------------------------------

*behave* can parse standard Gherkin files and extends Gherkin to allow
lowercase step keywords because these can sometimes allow more readable
feature specifications.

