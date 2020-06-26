.. _id.practicaltips:

=========================
Practical Tips on Testing
=========================

This chapter contains a collection of tips on test strategies and tools, such
as test automation libraries, that help you make BDD a successful experience.

Seriously, Don't Test the User Interface
========================================

.. warning::

    While you can use :pypi:`behave` to drive the "user interface" (UI) or
    front-end, interacting with the model layer or the business logic, e.g.
    by using a REST API, is often the better choice.

    And keep in mind, BDD advises your to test **WHAT** your application
    should do and not **HOW** it is done.

If you want to test/exercise also the "user interface", it may be a good idea
to reuse the feature files, that test the model layer, by just replacing the
test automation layer (meaning mostly the step implementations).
This approach ensures that your feature files are technology-agnostic,
meaning they are independent how you interact with "system under test" (SUT) or
"application under test" (AUT).

For example, if you want to use the feature files in the same directory for
testing the model layer and the UI layer, this can be done by using the
``--stage`` option, like with:

.. code-block:: console

    $ behave --stage=model features/
    $ behave --stage=ui    features/  # NOTE: Normally used on a subset of features.

See the :ref:`id.appendix.more_info` chapter for additional hints.

Automation Libraries
====================

With *behave* you can test anything on your application stack: front-end
behavior, RESTful APIs, you can even drive your unit tests using Gherkin
language.  Any library that helps you with that you usually integrate by
adding start-up code in ``before_all()`` and tear-down code in ``after_all()``.

The following examples show you how to interact with your Python application
by using the web interface (see `Seriously, Don't Test the User Interface`_
above to learn about entry points for test automation that may be better
suited for your use case).


Selenium (Example)
------------------

To start a web browser for interaction with the front-end using
:pypi:`selenium` your ``environment.py`` may look like this:

.. code-block:: python

    # -- FILE: features/environment.py
    # CONTAINS: Browser fixture setup and teardown
    from behave import fixture, use_fixture
    from selenium.webdriver import Firefox

    @fixture
    def browser_firefox(context):
        # -- BEHAVE-FIXTURE: Similar to @contextlib.contextmanager
        context.browser = Firefox()
        yield context.browser
        # -- CLEANUP-FIXTURE PART:
        context.browser.quit()

    def before_all(context):
        use_fixture(browser_firefox, context)
        # -- NOTE: CLEANUP-FIXTURE is called after after_all() hook.

In your step implementations you can use the ``context.browser`` object to
access Selenium features.  See the `Selenium docs`_ (``remote.webdriver``) for
details. Example using :pypi:`behave-django`:

.. code-block:: python

    # -- FILE: features/steps/browser_steps.py
    from behave import given, when, then

    @when(u'I visit "{url}"')
    def step_impl(context, url):
        context.browser.get(context.get_url(url))

.. _Selenium docs: https://seleniumhq.github.io/selenium/docs/api/py/api.html


Splinter (Example)
------------------

To start a web browser for interaction with the front-end using
:pypi:`splinter` your ``environment.py`` may look like this:

.. code-block:: python

    # -- FILE: features/environment.py
    # CONTAINS: Browser fixture setup and teardown
    from behave import fixture, use_fixture
    from splinter.browser import Browser

    @fixture
    def splinter_browser(context):
        context.browser = Browser()
        yield context.browser
        context.browser.quit()

    def before_all(context):
        use_fixture(splinter_browser, context)


In your step implementations you can use the ``context.browser`` object to
access Splinter features.  See the `Splinter docs`_ for details.  Example
using *behave-django*:

.. code-block:: python

    # -- FILE: features/steps/browser_steps.py
    from behave import given, when, then

    @when(u'I visit "{url}"')
    def step_impl(context, url):
        context.browser.visit(context.get_url(url))

.. _Splinter docs: https://splinter.readthedocs.io/en/latest/


Visual Testing
--------------

Visually checking your front-end on regression is integrated into *behave* in
a straight-forward manner, too.  Basically, what you do is drive your
application using the front-end automation library of your choice (such as
Selenium, Splinter, etc.) to the test location, take a screenshot and compare
it with an earlier, approved screenshot (your "baseline").

A list of visual testing tools and services is available from Dave Haeffner's
`How to Do Visual Testing`_ blog post.

.. _How to Do Visual Testing:
    https://applitools.com/blog/how-to-do-visual-testing-with-selenium
