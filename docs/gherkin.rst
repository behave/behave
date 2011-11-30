========================
Feature Testing Language
========================

.. if you change any headings in here make sure you haven't broken the
   cross-references in the API documentation or module docstrings!

*behave* uses a language called `Gherkin`_ to structure the ".feature" files.

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
