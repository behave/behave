=======================
Django Test Integration
=======================

There are now at least 2 projects that integrate `Django`_ and :pypi:`behave`.
Both use a `LiveServerTestCase`_ to spin up a runserver for the tests automatically,
and shut it down when done with the test run.  The approach used for integrating
Django, though, varies slightly.

:pypi:`behave-django`
    Provides a dedicated management command.  Easy, automatic integration (thanks
    to monkey patching).  Behave tests are run with ``python manage.py behave``.
    Allows running tests against an existing database as a special feature.
    See `setup <https://pythonhosted.org/behave-django/installation.html>`_
    and `usage <https://pythonhosted.org/behave-django/usage.html>`_ instructions.

:pypi:`django-behave`
    Provides a Django-specific TestRunner for Behave, which is set with the
    `TEST_RUNNER`_ property in your settings.  Behave tests are run
    with the usual ``python manage.py test <app_name>`` by default.
    See `setup <https://github.com/django-behave/django-behave/blob/master/README.md#how-to-use>`_
    instructions.

.. _Django: https://www.djangoproject.com
.. _LiveServerTestCase: https://docs.djangoproject.com/en/1.8/topics/testing/tools/#liveservertestcase
.. _TEST_RUNNER: https://docs.djangoproject.com/en/1.8/topics/testing/advanced/#using-different-testing-frameworks

Automation Libraries
====================

With *behave* you can test anything on the Django stack: front-end behavior,
REST APIs, you can even drive your unit tests using Gherkin language.
Any library that helps you with that you usually integrate by adding start-up
code in ``before_all()`` and tear-down code in ``after_all()``.

Selenium (Example)
------------------

To start a web browser for interaction with the front-end using
:pypi:`Selenium` your ``environment.py`` may look like this:

.. code-block:: python

   from selenium.webdriver import Firefox

   def before_all(context):
       context.browser = Firefox()

   def after_all(context):
       context.browser.quit()
       context.browser = None

In your step implementations you can use the ``context.browser`` object to
access Selenium features.  See the `Selenium docs`_ (``remote.webdriver``) for
details.  Example using *behave-django*:

.. code-block:: python

   @when(u'I visit "{url}"')
   def step_impl(context, url):
       context.browser.get(context.get_url(url))

.. _Selenium docs: http://selenium.googlecode.com/git/docs/api/py/api.html

Splinter (Example)
------------------

To start a web browser for interaction with the front-end using
:pypi:`Splinter` your ``environment.py`` may look like this:

.. code-block:: python

   from splinter.browser import Browser

   def before_all(context):
       context.browser = Browser()

   def after_all(context):
       context.browser.quit()
       context.browser = None

In your step implementations you can use the ``context.browser`` object to
access Splinter features.  See the `Splinter docs`_ for details.  Example
using *behave-django*:

.. code-block:: python

   @when(u'I visit "{url}"')
   def step_impl(context, url):
       context.browser.visit(context.get_url(url))


.. _Splinter docs: http://splinter.readthedocs.org/en/latest/

Visual Testing
--------------

Visually checking your front-end on regression is integrated into *behave* in
a straightforward manner, too.  Basically, what you do is drive your
application using the front-end automation library of your choice (such as
Selenium, Splinter, etc.) to the test location, take a screenshot and compare
it with an earlier, approved screenshot (your "baseline").

A list of visual testing tools and services is available from Dave Haeffner's
`How to Do Visual Testing`_ blog post.


.. _How to Do Visual Testing:
    http://testautomation.applitools.com/post/105435804567/how-to-do-visual-testing-with-selenium
