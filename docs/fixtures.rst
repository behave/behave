.. _docid.fixtures:

Fixtures
==============================================================================

A common task during test execution is to:

* setup a functionality when a test-scope is entered
* cleanup (or teardown) the functionality at the end of the test-scope

**Fixtures** are provided as concept to simplify this setup/cleanup task
in `behave`_.


Providing a Fixture
-------------------

.. code-block:: python

    # -- FILE: behave4my_project/fixtures.py  (or in: features/environment.py)
    from behave import fixture
    from somewhere.browser.firefox import FirefoxBrowser

    # -- FIXTURE-VARIANT 1: Use generator-function
    @fixture
    def browser_firefox(context, timeout=30, **kwargs):
        # -- SETUP-FIXTURE PART:
        context.browser = FirefoxBrowser(timeout, **kwargs)
        yield context.browser
        # -- CLEANUP-FIXTURE PART:
        context.browser.shutdown()

.. code-block:: python

    # -- FIXTURE-VARIANT 2: Use normal function
    from somewhere.browser.chrome import ChromeBrowser

    @fixture
    def browser_chrome(context, timeout=30, **kwargs):
        # -- SETUP-FIXTURE PART: And register as context-cleanup task.
        browser = ChromeBrowser(timeout, **kwargs)
        context.browser = browser
        context.add_cleanup(browser.shutdown)
        return browser
        # -- CLEANUP-FIXTURE PART: browser.shutdown()
        # Fixture-cleanup is called when current context-layer is removed.

.. seealso::

    A *fixture* is similar to:

    * a :func:`contextlib.contextmanager`
    * a `pytest.fixture`_
    * the `scope guard`_ idiom

.. include:: _common_extlinks.rst


Using a Fixture
---------------

In many cases, the usage of a fixture is triggered by the ``fixture-tag``
in a feature file. The ``fixture-tag`` marks that a fixture
should be used in this scenario/feature (as test-scope).

.. code-block:: gherkin

    # -- FILE: features/use_fixture1.feature
    Feature: Use Fixture on Scenario Level

        @fixture.browser.firefox
        Scenario: Use Web Browser Firefox
            Given I load web page "https://somewhere.web"
            ...
        # -- AFTER-SCENARIO: Cleanup fixture.browser.firefox

.. code-block:: gherkin

    # -- FILE: features/use_fixture2.feature
    @fixture.browser.firefox
    Feature: Use Fixture on Feature Level

        Scenario: Use Web Browser Firefox
            Given I load web page "https://somewhere.web"
            ...

        Scenario: Another Browser Test
            ...

    # -- AFTER-FEATURE: Cleanup fixture.browser.firefox


A **fixture** can be used by calling the :func:`~behave.use_fixture()` function.
The :func:`~behave.use_fixture()` call performs the ``SETUP-FIXTURE`` part and returns the
setup result. In addition, it ensures that ``CLEANUP-FIXTURE`` part is called
later-on when the current context-layer is removed.
Therefore, any manual cleanup handling in the ``after_tag()`` hook is not necessary.

.. code-block:: python

    # -- FILE: features/environment.py
    from behave import use_fixture
    from behave4my_project.fixtures import browser_firefox

    def before_tag(context, tag):
        if tag == "fixture.browser.firefox":
            use_fixture(browser_firefox, context, timeout=10)



Realistic Example
~~~~~~~~~~~~~~~~~

A more realistic example by using a fixture registry is shown below:

.. code-block:: python

    # -- FILE: features/environment.py
    from behave.fixture import use_fixture_by_tag, fixture_call_params
    from behave4my_project.fixtures import browser_firefox, browser_chrome

    # -- REGISTRY DATA SCHEMA 1: fixture_func
    fixture_registry1 = {
        "fixture.browser.firefox": browser_firefox,
        "fixture.browser.chrome":  browser_chrome,
    }
    # -- REGISTRY DATA SCHEMA 2: (fixture_func, fixture_args, fixture_kwargs)
    fixture_registry2 = {
        "fixture.browser.firefox": fixture_call_params(browser_firefox),
        "fixture.browser.chrome":  fixture_call_params(browser_chrome, timeout=12),
    }

    def before_tag(context, tag):
        if tag.startswith("fixture."):
            return use_fixture_by_tag(tag, context, fixture_registry1):
        # -- MORE: Tag processing steps ...


.. code-block:: python

    # -- FILE: behave/fixture.py
    # ...
    def use_fixture_by_tag(tag, context, fixture_registry):
        fixture_data = fixture_registry.get(tag, None)
        if fixture_data is None:
            raise LookupError("Unknown fixture-tag: %s" % tag)

        # -- FOR DATA SCHEMA 1:
        fixture_func = fixture_data
        return use_fixture(fixture_func, context)

        # -- FOR DATA SCHEMA 2:
        fixture_func, fixture_args, fixture_kwargs = fixture_data
        return use_fixture(fixture_func, context, *fixture_args, **fixture_kwargs)



.. hint:: **Naming Convention for Fixture Tags**

    Fixture tags should start with ``"@fixture.*"`` prefix to improve readability
    and understandibilty in feature files (Gherkin).

    Tags are used for different purposes. Therefore, it should be clear
    when a ``fixture-tag`` is used.



Fixture Cleanup Points
------------------------------------------------------------------------------

The point when a fixture-cleanup is performed depends on the scope where
:func:`~behave.use_fixture()` is called (and the fixture-setup is performed).


============= =========================== ==========================================================================================
Context Layer Fixture-Setup Point         Fixture-Cleanup Point
============= =========================== ==========================================================================================
test run      In ``before_all()`` hook    After ``after_all()``       at end of test-run.
feature       In ``before_feature()``     After ``after_feature()``,  at end of feature.
feature       In ``before_tag()``         After ``after_feature()``   for feature tag.
scenario      In ``before_scenario()``    After ``after_scenario()``, at end of scenario.
scenario      In ``before_tag()``         After ``after_scenario()``  for scenario tag.
scenario      In a step                   After ``after_scenario()``. Fixture is usable until end of scenario.
============= =========================== ==========================================================================================


Fixture Setup/Cleanup Semantics
------------------------------------------------------------------------------

If an error occurs during fixture-setup (meaning an exception is raised):

* Feature/scenario execution is aborted
* Any remaining fixture-setups are skipped
* After feature/scenario hooks are processed
* All fixture-cleanups and context cleanups are performed
* The feature/scenario is marked as failed

If an error occurs during fixture-cleanup (meaning an exception is raised):

* All remaining fixture-cleanups and context cleanups are performed
* First cleanup-error is reraised to pass failure to user (test runner)
* The feature/scenario is marked as failed



Ensure Fixture Cleanups with Fixture Setup Errors
------------------------------------------------------------------------------

Fixture-setup errors are special because a cleanup of a fixture is in many
cases not necessary (or rather difficult because the fixture object
is only partly created, etc.). Therefore, if an error occurs during fixture-setup
(meaning: an exception is raised), the fixture-cleanup part is normally not called.

If you need to ensure that the fixture-cleanup is performed, you need to
provide a slightly different fixture implementation:

.. code-block:: python

    # -- FILE: behave4my_project/fixtures.py  (or: features/environment.py)
    from behave import fixture
    from somewhere.browser.firefox import FirefoxBrowser

    def setup_fixture_part2_with_error(arg):
        raise RuntimeError("OOPS-FIXTURE-SETUP-ERROR-HERE)

    # -- FIXTURE-VARIANT 1: Use generator-function with try/finally.
    @fixture
    def browser_firefox(context, timeout=30, **kwargs):
        try:
            browser = FirefoxBrowser(timeout, **kwargs)
            browser.part2 = setup_fixture_part2_with_error("OOPS")
            context.browser = browser   # NOT_REACHED
            yield browser
            # -- NORMAL FIXTURE-CLEANUP PART: NOT_REACHED due to setup-error.
         finally:
            browser.shutdown()  # -- CLEANUP: When generator-function is left.

.. code-block:: python

    # -- FIXTURE-VARIANT 2: Use normal function and register cleanup-task early.
    from somewhere.browser.chrome import ChromeBrowser

    @fixture
    def browser_chrome(context, timeout=30, **kwargs):
        browser = ChromeBrowser(timeout, **kwargs)
        context.browser = browser
        context.add_cleanup(browser.shutdown)   # -- ENSURE-CLEANUP EARLY
        browser.part2 = setup_fixture_part2_with_error("OOPS")
        return browser  # NOT_REACHED
        # -- CLEANUP: browser.shutdown() when context-layer is removed.

.. note::

    An fixture-setup-error that occurs when the browser object is created,
    is not covered by these solutions and not so easy to solve.



Composite Fixtures
------------------------------------------------------------------------------

The last section already describes some problems when you use
complex or *composite fixtures*. It must be ensured that cleanup of already
created fixture parts is performed even when errors occur late in the creation
of a *composite fixture*. This is basically a `scope guard`_ problem.

Solution 1:
~~~~~~~~~~~

.. code-block:: python

    # -- FILE: behave4my_project/fixtures.py
    # SOLUTION 1: Use "use_fixture()" to ensure cleanup even in case of errors.
    from behave import fixture, use_fixture

    @fixture
    def foo(context, *args, **kwargs):
        pass    # -- FIXTURE IMPLEMENTATION: Not of interest here.

    @fixture
    def bar(context, *args, **kwargs):
        pass    # -- FIXTURE IMPLEMENTATION: Not of interest here.

    # -- SOLUTION: With use_fixture()
    # ENSURES: foo-fixture is cleaned up even when setup-error occurs later.
    @fixture
    def composite1(context, *args, **kwargs):
        the_fixture1 = use_fixture(foo, context)
        the_fixture2 = use_fixture(bar, context)
        return [the_fixture1, the_fixture2]


Solution 2:
~~~~~~~~~~~

.. code-block:: python

    # -- ALTERNATIVE SOLUTION: With use_composite_fixture_with()
    from behave import fixture
    from behave.fixture import use_composite_fixture_with, fixture_call_params

    @fixture
    def composite2(context, *args, **kwargs):
        the_composite = use_composite_fixture_with(context, [
            fixture_call_params(foo, name="foo"),
            fixture_call_params(bar, name="bar"),
        ])
        return the_composite


