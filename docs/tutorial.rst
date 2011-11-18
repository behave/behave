=================
Tutorial, behave!
=================

To make behave work for you create a directory called "features"
containing:

1. `feature files`_ written by your Business Analyst / Sponsor / whoever
   with your behaviour scenarios in it, and
2. a "steps" directory with `Python step implementations`_ for the
   scenarios.

You may optionally include some `environmental controls`_ (code to run
before and after steps, scenarios, features or the whole shooting
match).

A typical "features" directory tree might look like::

  features/
  features/signup.feature
  features/login.feature
  features/account_details.feature
  features/environment.py
  features/steps/
  features/steps/website.py
  features/steps/utils.py


Feature Files
=============

A feature file has a simple format describing a feature or part of a
feature with representative examples of expected outcomes. They're
plain-text and look something like::

  Feature: Fight or flight
    In order to increase the ninja survival rate,
    As a ninja commander
    I want my ninjas to decide whether to take on an 
    opponent based on their skill levels

    Scenario: Weaker opponent
      Given the ninja has a third level black-belt 
      When attacked by a samurai
      Then the ninja should engage the opponent

    Scenario: Stronger opponent
      Given the ninja has a third level black-belt 
      When attacked by Chuck Norris
      Then the ninja should run for his life

The "Given", "When" and "Then" parts of this prose form the actual steps
that will be taken by *behave* in testing your system. These map to `Python
step implementations`_.


Python Step Implementations
===========================

Steps used in the scenarios are implemented in Python files in
"features/steps". You can call these whatever you like
as long as they're *filename*.py in the steps directory.

Steps are identified using decorators which match the predicate from the
feature file: Given, When and Then. The decorator accepts a string
containing the rest of the phrase used in the scenario step it belongs to.

Given a Scenario::

  Scenario: Search for an account
     Given I search for a valid account
      Then I will see the account details

Step code implementing the two steps here might look like (using selenium
webdriver and some other helpers)::

 @Given('I search for a valid account')
 def step(context):
    context.browser.get('http://localhost:8000/index')
    form = get_element(context.browser, tag='form')
    get_element(form, name="jt_msisdn").send_keys('61415551234)
    form.submit()

 @Then('I will see the account details')
 def step(context):
    elements = find_elements(context.browser, id='no-account')
    eq_(elements, [], 'account not found')
    h = get_element(context.browser, id='account-head')
    ok_(h.text.startswith("Account 61415551234"),
        'Heading %r has wrong text' % h.text)


Environmental Controls
======================

The environment.py module may define code to run before and after certain
events during your testing:

**before_step(context, step), after_step(context, step)**
  These run before and after every step.
**before_scenario(context, scenario), after_scenario(context, scenario)**
  These run before and after each scenario is run.
**before_feature(context, feature), after_feature(context, feature)**
  These run before and after each feature file is exercised.
**before_all(context), after_all(context)**
  These run before and after the whole shooting match.

The feature, scenario and step objects represent the information parsed
from the feature file.

.. todo: document what those objects might be

A common use-case for environmental controls might be to set up a web
server and browser to run all your tests in. For example::

  import threading
  from wsgiref import simple_server
  from selenium import webdriver
  import my_application import model
  import my_application import web_app

  def before_all(context):
      context.server = simple_server.WSGIServer(('', 8000))
      context.server.set_app(web_app.main(environment='test'))
      context.thread = threading.Thread(target=context.server.serve_forever)
      context.thread.start()
      context.browser = webdriver.Chrome()

  def after_all(context):
      context.server.shutdown()
      context.thread.join()
      context.browser.quit()

  def before_feature(context, feature):
      model.init(environment='test')

Of course if you wish you could have a new browser for each feature, or to
retain the database state between features or even initialise the database
for to each scenario.

