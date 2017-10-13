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
    See `setup behave-django <https://pythonhosted.org/behave-django/installation.html>`_
    and `usage <https://pythonhosted.org/behave-django/usage.html>`_ instructions.

:pypi:`django-behave`
    Provides a Django-specific TestRunner for Behave, which is set with the
    `TEST_RUNNER`_ property in your settings.  Behave tests are run
    with the usual ``python manage.py test <app_name>`` by default.
    See `setup django-behave <https://github.com/django-behave/django-behave/blob/master/README.md#how-to-use>`_
    instructions.

.. _Django: https://www.djangoproject.com
.. _LiveServerTestCase: https://docs.djangoproject.com/en/1.8/topics/testing/tools/#liveservertestcase
.. _TEST_RUNNER: https://docs.djangoproject.com/en/1.8/topics/testing/advanced/#using-different-testing-frameworks


Manual Integration
==================

Alternatively, you can integrate Django using the following boilerplate code
in your ``environment.py`` file:

.. code-block:: python

    # -- FILE: features/environment.py
    import os
    import django
    from django.test.runner import DiscoverRunner
    from django.test.testcases import LiveServerTestCase

    os.environ["DJANGO_SETTINGS_MODULE"] = "test_project.settings"

    def before_all(context):
        django.setup()
        context.test_runner = DiscoverRunner()
        context.test_runner.setup_test_environment()
        context.old_db_config = context.test_runner.setup_databases()

    def before_scenario(context, scenario):
        context.test_case = LiveServerTestCase
        context.test_case.setUpClass()

    def after_scenario(context, scenario):
        context.test_case.tearDownClass()
        del context.test_case

    def after_all(context):
        context.test_runner.teardown_databases(context.old_db_config)
        context.test_runner.teardown_test_environment()

Taken from Andrey Zarubin's blog post "`BDD. PyCharm + Python & Django`_".

.. _`BDD. PyCharm + Python & Django`:
    https://anvileight.com/blog/2016/04/12/behavior-driven-development-pycharm-python-django/


Strategies and Tooling
======================

See :ref:`id.practicaltips` for automation libraries and implementation tips
on your BDD tests.
