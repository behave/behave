=======================
Django Test Integration
=======================

There are now at least 2 projects that integrate `Django`_ and :pypi:`behave`.  
Both use a `LiveServerTestCase`_ to spin up a runserver for the tests automatically, 
and shut it down when done with the test run.  The approach used for integrating
Django, though, varies slightly.

:pypi:`behave-django`
    Integrates Django via setup code in your Behave ``environment.py`` file.
    Behave tests are invoked with a dedicated ``python manage.py behave``
    command by default.

:pypi:`django-behave`
    Provides a Django-specific TestRunner for Behave, which is set with the
    `TEST_RUNNER`_ property in your settings.  Behave tests are run
    with the usual ``python manage.py test <app_name>`` by default.

.. _Django: https://www.djangoproject.com
.. _LiveServerTestCase: https://docs.djangoproject.com/en/1.8/topics/testing/tools/#liveservertestcase
.. _TEST_RUNNER: https://docs.djangoproject.com/en/1.8/topics/testing/advanced/#using-different-testing-frameworks


Manual Integration
================================

The approach that is shown here provides a manual integration.
It serves as basic example how such a functionality can be provided.
In general, it is probably better to use one of the projects above.

This example uses:

- :pypi:`mechanize` to pretend to be a web browser
- :pypi:`wsgi_intercept` to install a WSGI application in place of a real URI for testing
- :pypi:`BeautifulSoup` to parse the HTML fetched by the fake browser
  (substitute lxml or html5lib as you see fit)


This is based on Nathan Reynolds' `Mechanize support for Django testcases`__
and was developed by David Eyk in a `public gist`__.

__ https://github.com/nathforge/django-mechanize/
__ https://gist.github.com/eykd/1637965


Implementation
--------------

`Features`__ file "features/browser.feature":

.. code-block:: gherkin

    # -- FILE: features/browser.feature
    Feature: Demonstrate how to test Django with behave & mechanize

      Scenario: Logging in to our new Django site

        Given a user
         When I log in
         Then I see my account summary
          And I see a warm and welcoming message

__ tutorial.html#feature-files

`Steps Python code`__ "features/steps/browser.py":

.. code-block:: python

    # -- FILE: features/steps/browser.py
    from behave import given, when, then

    @given('a user')
    def step_impl(context):
        from django.contrib.auth.models import User
        u = User(username='foo', email='foo@example.com')
        u.set_password('bar')

    @when('I log in')
    def step_impl(context):
        br = context.browser
        br.open(context.browser_url('/account/login/'))
        br.select_form(nr=0)
        br.form['username'] = 'foo'
        br.form['password'] = 'bar'
        br.submit()

    @then('I see my account summary')
    def step_impl(context):
        br = context.browser
        response = br.response()
        assert response.code == 200
        assert br.geturl().endswith('/account/')

    @then('I see a warm and welcoming message')
    def step_impl(context):
        # Remember, context.parse_soup() parses the current response in
        # the mechanize browser.
        soup = context.parse_soup()
        msg = str(soup.findAll('h2', attrs={'class': 'welcome'})[0])
        assert "Welcome, foo!" in msg

__ tutorial.html#python-step-implementations

`Environment setup`__ in "features/environment.py":

.. code-block:: python
    
    # -- FILE: features/environment.py
    import os
    # This is necessary for all installed apps to be recognized, for some reason.
    os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'


    def before_all(context):
        # Even though DJANGO_SETTINGS_MODULE is set, this may still be
        # necessary. Or it may be simple CYA insurance.
        from django.core.management import setup_environ
        from myproject import settings
        setup_environ(settings)

        ### Take a TestRunner hostage.
        from django.test.simple import DjangoTestSuiteRunner
        # We'll use this later to frog-march Django through the motions
        # of setting up and tearing down the test environment, including
        # test databases.
        context.runner = DjangoTestSuiteRunner()

        ## If you use South for migrations, uncomment this to monkeypatch
        ## syncdb to get migrations to run.
        # from south.management.commands import patch_for_test_db_setup
        # patch_for_test_db_setup()

        ### Set up the WSGI intercept "port".
        import wsgi_intercept
        from django.core.handlers.wsgi import WSGIHandler
        host = context.host = 'localhost'
        port = context.port = getattr(settings, 'TESTING_MECHANIZE_INTERCEPT_PORT', 17681)
        # NOTE: Nothing is actually listening on this port. wsgi_intercept
        # monkeypatches the networking internals to use a fake socket when
        # connecting to this port.
        wsgi_intercept.add_wsgi_intercept(host, port, WSGIHandler)

        def browser_url(url):
            """Create a URL for the virtual WSGI server.

            e.g context.browser_url('/'), context.browser_url(reverse('my_view'))
            """
            return urlparse.urljoin('http://%s:%d/' % (host, port), url)

        context.browser_url = browser_url

        ### BeautifulSoup is handy to have nearby. (Substitute lxml or html5lib as you see fit)
        from BeautifulSoup import BeautifulSoup
        def parse_soup():
            """Use BeautifulSoup to parse the current response and return the DOM tree.
            """
            r = context.browser.response()
            html = r.read()
            r.seek(0)
            return BeautifulSoup(html)

        context.parse_soup = parse_soup


    def before_scenario(context, scenario):
        # Set up the scenario test environment
        context.runner.setup_test_environment()
        # We must set up and tear down the entire database between
        # scenarios. We can't just use db transactions, as Django's
        # TestClient does, if we're doing full-stack tests with Mechanize,
        # because Django closes the db connection after finishing the HTTP
        # response.
        context.old_db_config = context.runner.setup_databases()

        ### Set up the Mechanize browser.
        from wsgi_intercept import mechanize_intercept
        # MAGIC: All requests made by this monkeypatched browser to the magic
        # host and port will be intercepted by wsgi_intercept via a
        # fake socket and routed to Django's WSGI interface.
        browser = context.browser = mechanize_intercept.Browser()
        browser.set_handle_robots(False)


    def after_scenario(context, scenario):
        # Tear down the scenario test environment.
        context.runner.teardown_databases(context.old_db_config)
        context.runner.teardown_test_environment()
        # Bob's your uncle.

__ tutorial.html#environmental-controls
