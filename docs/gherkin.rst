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

*behave* uses a language called `Gherkin`_ to structure the "*name*.feature" files.

These files should be written using natural language - ideally by the
non-technical business participants in the software project.

It is very flexible but has a few simple rules that writers need to adhere to.

.. _`gherkin`: TODO


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
scope issue in the feature name.

.. any other advice we could include here?

The Background and Scenarios will be discussed in the following sections.


Backgrounds
-----------

A background is a series of steps to be executed before the scenarios for
the feature are tested. It is run just once, and is useful for performing
setup operations like logging into a web browser or setting up a database
with test data used by the scenarios.

Again the background name should just be a reasonably descriptive title
for the background operation being performed or requirement being met.

The background is not tested for failure. If it's something that can fail
then it probably should be a scenario to be tested.

It contains `steps`_ as described below.


Scenarios
---------

Scenarios describe the discrete behaviours being tested.


TODO

It is good practise to have them test only one behaviour each.

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

Steps take a line each and begin with a *keyword* 

TODO

They should not need to contain significant degree of detail about the
mechanics of testing; that is, instead of:

.. code-block:: gherkin

  Given a browser client is used to load the URL "http://website.example/website/home.html"

the step could instead simply say:

.. code-block:: gherkin

  Given we are looking at the home page


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


