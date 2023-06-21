behave i18n (gherkin-languages.json)
=====================================================================================

`behave`_ uses the official `cucumber`_ `gherkin-languages.json`_ file 
to keep track of step keywords for any I18n spoken language.

Use the following procedure if any language keywords are missing/should-be-corrected, etc.

**PROCEDURE:**

* Make pull-request on: https://github.com/cucumber/gherkin repository
* After it is merged, I pull the new version of `gherkin-languages.json` and generate `behave/i18n.py` from it
* OPTIONAL: Give an info that it is merged (if I am missing this state-change)

SEE ALSO:

* https://github.com/cucumber/gherkin
* https://github.com/cucumber/gherkin/blob/main/gherkin-languages.json
* https://raw.githubusercontent.com/cucumber/gherkin/main/gherkin-languages.json

.. _behave: https://github.com/behave/behave
.. _cucumber: https://github.com/cucumber/common
.. _gherkin-languages.json: https://github.com/cucumber/gherkin/blob/main/gherkin-languages.json
