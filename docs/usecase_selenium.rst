=============================
Selenium and Page Objects
=============================

If you test web applications with `Selenium`_, you probably have a pile of
step definitions that find elements and fill forms. It works at first.
Then the page changes and half your steps break.

The `Page Object Model`_ is a pattern that fixes this. You wrap each page's
locators and interactions in a class. Your steps talk to that class instead of
poking at the DOM directly. When the page changes, you update one file, not
twenty. Selenium's own docs `encourage this pattern`_. This guide walks
through a basic setup with behave.

.. _Selenium: https://www.selenium.dev/
.. _`Page Object Model`: https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/
.. _`encourage this pattern`: https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/


Project Layout
==============

A typical project looks like this::

    features/
        login.feature
        search.feature
        steps/
            login_steps.py
            search_steps.py
        pages/
            __init__.py
            base_page.py
            login_page.py
            search_page.py
        environment.py

The ``pages/`` directory holds your page object classes. The ``steps/``
directory imports them. Steps describe the test in plain language; page objects
deal with the DOM.


A Base Page
===========

Start with a base class that wraps the WebDriver. This keeps the boilerplate
in one place:

.. code-block:: python

    # -- FILE: features/pages/base_page.py
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException


    class BasePage:
        def __init__(self, driver):
            self.driver = driver
            self.wait = WebDriverWait(driver, timeout=10)

        def open(self, url):
            self.driver.get(url)

        def find(self, locator):
            return self.driver.find_element(*locator)

        def click(self, locator):
            self.find(locator).click()

        def type_text(self, locator, text):
            element = self.find(locator)
            element.clear()
            element.send_keys(text)

        def wait_for_visible(self, locator):
            self.wait.until(EC.visibility_of_element_located(locator))

        def get_text(self, locator):
            return self.find(locator).text

        def is_visible(self, locator):
            try:
                self.wait_for_visible(locator)
                return True
            except TimeoutException:
                return False


Nothing fancy. Just the things every page needs.


A Login Page
============

Build a page object for a login screen:

.. code-block:: python

    # -- FILE: features/pages/login_page.py
    from selenium.webdriver.common.by import By
    from features.pages.base_page import BasePage


    class LoginPage(BasePage):
        URL = "/login"

        USERNAME_INPUT = (By.ID, "username")
        PASSWORD_INPUT = (By.ID, "password")
        SUBMIT_BUTTON = (By.ID, "login-submit")
        ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-danger")

        def open_login_page(self, base_url):
            self.open(base_url + self.URL)

        def login(self, username, password):
            self.type_text(self.USERNAME_INPUT, username)
            self.type_text(self.PASSWORD_INPUT, password)
            self.click(self.SUBMIT_BUTTON)

        def get_error(self):
            return self.get_text(self.ERROR_MESSAGE)

        def is_loaded(self):
            return self.is_visible(self.USERNAME_INPUT)

.. note::

    ``wait_for_visible`` uses ``visibility_of_element_located``, which checks
    that the element is both present in the DOM and actually displayed. Use
    ``presence_of_element_located`` only when you don't care about visibility
    (for example, hidden inputs).


Each locator lives here, not in the step file. If the login form's button ID
changes from ``login-submit`` to ``btn-login``, you change one line in
``LoginPage`` and every step that uses the login page keeps working.


Wiring It Up in environment.py
==============================

Set up the WebDriver once, in ``before_all``, and tear it down in
``after_all``. Store the driver on ``context`` so steps can pass it to page
objects:

.. code-block:: python

    # -- FILE: features/environment.py
    from selenium import webdriver


    def before_all(context):
        context.driver = webdriver.Chrome()

    def after_all(context):
        context.driver.quit()


You can also scope the driver per scenario if you want a fresh browser each
time:

.. code-block:: python

    def before_scenario(context, scenario):
        context.driver = webdriver.Chrome()

    def after_scenario(context, scenario):
        context.driver.quit()


A shared browser is faster. A fresh browser per scenario avoids state
leaking between tests. Use whichever fits your situation. One thing to watch
out for: the ``BasePage`` class above uses ``WebDriverWait`` for explicit
waits. Don't combine that with ``driver.implicitly_wait()`` -- the two wait
strategies can stack and cause unpredictable timeouts. Stick to one.
Explicit waits (``WebDriverWait``) are the better choice in modern Selenium.


Writing the Steps
=================

The feature file stays readable:

.. code-block:: gherkin

    # -- FILE: features/login.feature
    Feature: Login

      Scenario: Valid user can log in
        Given I am on the login page
        When I log in with "alice" and "secret123"
        Then I should see the dashboard

      Scenario: Wrong password shows an error
        Given I am on the login page
        When I log in with "alice" and "wrongpass"
        Then I should see the error "Invalid credentials"

The step definitions stay thin. They hand the driver to a page object and
check what comes back:

.. code-block:: python

    # -- FILE: features/steps/login_steps.py
    from behave import given, when, then
    from features.pages.login_page import LoginPage


    @given("I am on the login page")
    def step_on_login_page(context):
        page = LoginPage(context.driver)
        base_url = context.config.userdata.get("base_url", "http://localhost:8000")
        page.open_login_page(base_url)
        assert page.is_loaded(), "Login page did not load"


    @when('I log in with "{username}" and "{password}"')
    def step_login(context, username, password):
        page = LoginPage(context.driver)
        page.login(username, password)


    @then('I should see the error "{text}"')
    def step_should_see_error(context, text):
        page = LoginPage(context.driver)
        assert text in page.get_error()


    @then("I should see the dashboard")
    def step_should_see_dashboard(context):
        # -- Check that the URL changed or a dashboard element is visible.
        assert "dashboard" in context.driver.current_url


Notice what the steps don't do: no ``find_element`` calls, no CSS selectors.
That's all inside the page object. The step reads almost like the feature
file -- which is the point. A reader who knows the Gherkin can follow the
step logic without knowing Selenium.


Tips
====

* Keep page objects small. If a page object grows past 100 lines, split it.
  A ``SearchResultsPage`` that also handles filters and pagination is two or
  three classes, not one.

* Don't put assertions in page objects. Return values and let the steps
  check them. You may want the same page object in one test that expects an
  error and another that expects success.

* Use ``context`` to share page objects between steps when it makes sense.
  For example, store the current page so the next step can pick up where the
  last one left off:

  .. code-block:: python

      @given("I am on the login page")
      def step_on_login_page(context):
          page = LoginPage(context.driver)
          base_url = context.config.userdata.get("base_url", "http://localhost:8000")
          page.open_login_page(base_url)
          context.page = page

* If you need a headless browser for CI, pass the option through
  ``context.config.userdata`` (with ``-D`` on the command line) or an
  environment variable. Don't hardcode it.


Related
=======

* `behave-django page objects`_ -- behave-django has experimental support
  for page objects, with links to related libraries.
* `Page Object Model (Selenium docs)`_ -- the official Selenium guide.

.. _`behave-django page objects`:
    https://behave-django.readthedocs.io/en/stable/pageobject.html
.. _`Page Object Model (Selenium docs)`:
    https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/
