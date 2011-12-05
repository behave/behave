===========================
Comparison With Other Tools
===========================

There are other options for doing Gherkin-based BDD in Python. We've listed
the main ones below and why we feel you're better off using behave. Obviously
this comes from our point of view and you may disagree. That's cool. We're
not worried whichever way you go.

This page may be out of date as the projects mentioned will almost certainly
change over time. If anything on this page is out of date, please contact us.

Cucumber_
=========

You can actually use Cucumber to run test code written in Python. It uses
rubypython_ to fire up a Python interpreter inside the Ruby process though and
this can be somewhat brittle. Obviously we prefer to use something written in
Python but if you've got an existing workflow based around Cucumber and you
have code in multiple languages, Cucumber may be the one for you.

.. _Cucumber: http://cukes.info/
.. _rubypython: http://rubypython.rubyforge.org/

Lettuce_
========

Lettuce is similar to behave in that it's a fairly straight port of the basic
functionality of Cucumber. The main differences with behave are:

* Single decorator for step definitions, ``@step``.
* The context variable, ``world``, is simply a shared holder of attributes. It
  never gets cleaned up during the run.
* Hooks are declared using decorators rather than as simple functions.
* No support for tags.
* Step definition code files can be anywhere in the feature directory
  hierarchy.

The issues we had with Lettuce that stopped us using it were:

* Lack of tags.
* The hooks functionality was patchy. For instance it was very hard to clean
  up the ``world`` variable between scenario outlines. Behave clears the
  scenario-level context between outlines automatically.
* Lettuce's handling of stdout would occasionally cause it to crash mid-run in
  such a way that cleanup hooks were never run.
* Lettuce uses import hackery so .pyc files are left around and the module
  namespace is polluted.

.. _Lettuce: http://lettuce.it/

Freshen_
========

Freshen is a plugin for nose_ that implements a Gherkin-style language with
Python step definitions. The main differences with behave are:

* Operates as a plugin for nose, and is thus tied to the nose runner and its
  output model.
* Has some additions to its Gherkin syntax allowing it to specify specific step
  definition modules for each feature.
* Has separate context objects for various levels: ``glc``, ``ftc`` and
  ``scc``. These relate to global, feature and scenario levels respectively.

The issues we had with Freshen that suppoed us using it were:

* The integration with the nose runner made it quite hard to properly debug
  how and why tests were failing. Quite often you'd get a rather cryptic
  message with the actual exception having been swallowed.
* The feature-specific step includes could lead to specific sets of step
  definitions for each feature despite them warning against doing that.
* The output being handled by nose meant that you couldn't do cucumber-style
  output without the addition of more plugins.
* The context variable names are cryptic and moving context data from one
  level to another takes a certain amount of work finding and renaming. The
  behave `context` variable is much more flexible.
* Step functions must have unique names, even though they're decorated to
  match different strings.
* As with Lettuce, Freshen uses import hackery so .pyc files are left
  around and the module namespace is polluted.
* Only Before and no contextual before/after control, thus requiring use of
  atexit for teardown operations and no fine-grained control.

The above being said the integration with nose means that you gain things like
JUnit output and coverage analysis fairly easily. This may or may not be an
issue for you. Behave will be adding JUnit output soon and we will more than
likely forget to remove this sentence when we do.

.. _Freshen: https://github.com/rlisagor/freshen
.. _nose: http://readthedocs.org/docs/nose/
.. _parse: http://pypi.python.org/pypi/parse
