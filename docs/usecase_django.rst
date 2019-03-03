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
    See `setup behave-django <https://behave-django.readthedocs.io/en/latest/installation.html>`_
    and `usage <https://behave-django.readthedocs.io/en/latest/usage.html>`_ instructions.

:pypi:`django-behave`
    Provides a Django-specific TestRunner for Behave, which is set with the
    `TEST_RUNNER`_ property in your settings.  Behave tests are run
    with the usual ``python manage.py test <app_name>`` by default.
    See `setup django-behave <https://github.com/django-behave/django-behave/blob/master/README.md#how-to-use>`_
    instructions.

.. _Django: https://www.djangoproject.com
.. _LiveServerTestCase: https://docs.djangoproject.com/en/stable/topics/testing/tools/#liveservertestcase
.. _TEST_RUNNER: https://docs.djangoproject.com/en/stable/topics/testing/advanced/#using-different-testing-frameworks


Manual Integration
==================

Alternatively, you can integrate Django using the following boilerplate code
in your ``environment.py`` file:

.. code-block:: python

    # -- FILE: my_django/behave_fixtures.py
    from behave import fixture
    import django
    from django.test.runner import DiscoverRunner
    from django.test.testcases import LiveServerTestCase

    @fixture
    def django_test_runner(context):
        django.setup()
        context.test_runner = DiscoverRunner()
        context.test_runner.setup_test_environment()
        context.old_db_config = context.test_runner.setup_databases()
        yield
        context.test_runner.teardown_databases(context.old_db_config)
        context.test_runner.teardown_test_environment()

    @fixture
    def django_test_case(context):
        context.test_case = LiveServerTestCase
        context.test_case.setUpClass()
        yield
        context.test_case.tearDownClass()
        del context.test_case


.. code-block:: python

    # -- FILE: features/environment.py
    from behave import use_fixture
    from my_django.behave_fixtures import django_test_runner, django_test_case
    import os

    os.environ["DJANGO_SETTINGS_MODULE"] = "test_project.settings"

    def before_all(context):
        use_fixture(django_test_runner, context)

    def before_scenario(context, scenario):
        use_fixture(django_test_case, context)


Taken and adapted from Andrey Zarubin's blog post "`BDD. PyCharm + Python & Django`_".

.. _`BDD. PyCharm + Python & Django`:
    https://blog.anvileight.com/posts/behavior-driven-development-pycharm-python-django/


Strategies and Tooling
======================

See :ref:`id.practicaltips` for automation libraries and implementation tips
on your BDD tests.
