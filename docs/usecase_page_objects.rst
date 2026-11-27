============
Page Objects
============

If you automate browser tests, you probably have a pile of step definitions
that find elements and fill forms. It works at first. Then the page changes
and half your steps break.

The `Page Object Model`_ is a pattern that fixes this. You wrap each page's
locators and interactions in a class. Your steps talk to that class instead of
poking at the page directly. When the page changes, you update one file, not
twenty.

The same structure works with any driver. This guide explains the pattern in
tool-agnostic terms, then shows a complete example with `Selenium`_ at the
end.

.. _Selenium: https://www.selenium.dev/
.. _`Page Object Model`: https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/


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

``pages/`` holds your page object classes. ``steps/`` imports them. Steps
describe the test in plain language; page objects handle the driver and
locators.


A Base Page
===========

Every page object needs a reference to the driver, a way to wait for
elements, and a few helper methods. Put those in a base class:

.. code-block:: python

    # -- FILE: features/pages/base_page.py
    class BasePage:
        def __init__(self, driver):
            self.driver = driver

        def open(self, url):
            """Navigate to a URL."""

        def find(self, locator):
            """Return the element for a locator."""

        def click(self, locator):
            """Click an element."""

        def type_text(self, locator, text):
            """Clear an element and type text into it."""

        def wait_for_visible(self, locator):
            """Block until the element is visible."""

        def get_text(self, locator):
            """Return the text content of an element."""

        def is_visible(self, locator):
            """Return True if the element is visible, False otherwise."""

How you fill in those methods depends on your driver. Every page object in
your project inherits from this class, so the boilerplate lives in one place.


A Login Page
============

A page object for a login screen needs locators for the form fields and the
error message. It also needs methods to fill the form and read back the
result:

.. code-block:: python

    # -- FILE: features/pages/login_page.py
    class LoginPage(BasePage):
        URL = "/login"

        # -- Locators (tool-specific)
        USERNAME_INPUT = ...
        PASSWORD_INPUT = ...
        SUBMIT_BUTTON = ...
        ERROR_MESSAGE = ...

        def open_login_page(self, base_url):
            """Navigate to the login page."""

        def login(self, username, password):
            """Fill the form and submit."""

        def get_error(self):
            """Return the error message text."""

        def is_loaded(self):
            """Return True if the login form is visible."""

Each locator lives here, not in the step file. Change one line in
``LoginPage`` and every step that uses the page keeps working.


Wiring It Up in environment.py
==============================

Create the driver once and store it on ``context`` so steps can pass it to
page objects. Set it up in ``before_all``, tear it down in ``after_all``:

.. code-block:: python

    # -- FILE: features/environment.py
    def before_all(context):
        context.driver = create_driver()

    def after_all(context):
        context.driver.quit()

You can also scope the driver per scenario if you want a fresh browser each
time:

.. code-block:: python

    def before_scenario(context, scenario):
        context.driver = create_driver()

    def after_scenario(context, scenario):
        context.driver.quit()

A shared browser is faster. A fresh browser per scenario avoids state
leaking between tests. Use whichever fits your situation.


Writing the Steps
=================

Your feature file stays clean:

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

Step definitions stay thin. They hand the driver to a page object and check
what comes back:

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
file, which is the point. A reader who knows the Gherkin can follow the step
logic without knowing anything about the driver underneath.


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
  environment variable. Don't hardcode it. The same goes for browser choice
  -- read it from config instead of locking it into the page object.

* If you swap the driver later (say, from Selenium to Playwright), only the
  page objects change. The feature files and step definitions stay the same.
  That is the main payoff of this pattern.


Full Example with Selenium
==========================

.. note::

    BDD is not tied to browser automation, and browser automation is not
    BDD. Behave drives your tests. The page object pattern just keeps the
    automation details out of your step definitions. The Selenium example
    below is one way to implement it, nothing more.

Here is the same pattern filled in with `Selenium`_. The base page uses
``WebDriverWait`` for explicit waits and ``expected_conditions`` to check
visibility.

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

For locators, the login page uses ``By.ID`` and ``By.CSS_SELECTOR``:

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

``environment.py`` creates a Chrome instance:

.. code-block:: python

    # -- FILE: features/environment.py
    from selenium import webdriver


    def before_all(context):
        context.driver = webdriver.Chrome()

    def after_all(context):
        context.driver.quit()

.. note::

    ``wait_for_visible`` uses ``visibility_of_element_located``, which checks
    that the element is both present in the DOM and actually displayed. Use
    ``presence_of_element_located`` only when you don't care about visibility
    (for example, hidden inputs).

.. note::

    Don't combine ``WebDriverWait`` with ``driver.implicitly_wait()``. The two
    wait strategies can stack and cause unpredictable timeouts. Stick to one.
    Explicit waits are the better choice in modern Selenium.


Related
=======

* `behave-django page objects`_ -- behave-django has experimental support
  for page objects, with links to related libraries.
* `Page Object Model (Selenium docs)`_ -- the official Selenium guide. The
  pattern is the same regardless of which tool you use.

.. _`behave-django page objects`:
    https://behave-django.readthedocs.io/en/stable/pageobject.html
.. _`Page Object Model (Selenium docs)`:
    https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/
