=======
Behave!
=======

Behave aids Behaviour Driven Development. 

To make behave work for you create a directory called "features"
containing:

1. `feature files`_ written by your Business Analyst / Sponsor / whoever
   with your behaviour scenarios in it, and
2. a "steps" directory with `Python step implementations`_ for the
   scenarios.

You may optionally include some `environment controls`_ (code to run
before and after steps, scenarios, features or the whole shooting
match).

A typical "features" directory tree might look like:

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

Benno can fill this bit in :-)


Python Step Implementations
===========================

Steps used in the scenarios are implemented in Python files in
"features/steps". You can call these whatever you like
as long as they're *filename*.py in the steps directory.

Steps are identified using


Environmental Controls
======================

The environment.py module may define code to run before and after certain
events during your testing:

**before_step, after_step**
  These run before and after every step.
**before_scenario, after_scenario**
  These run before and after the whole shooting match.
**before_feature, after_feature**
  These run before and after the whole shooting match.
**before_all, after_all**
  These run before and after the whole shooting match.

