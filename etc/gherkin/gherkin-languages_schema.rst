Schema Comparison of "gherkin-languages.json" vs "i18n.yml"
=============================================================================


Schema Comparison
-----------------------------------------------------------------------------

* i18n.yaml: Keywords and Step keywords need to be split w/ "|" (pipe)
* Step keywords have extra trailing space (in: "gherkin-languages.json")
  except for some languages that do not need a whitespace character as separator
  (like: "zh-CN", "zh-TW", "ja", "ta", "ro", "ko", "ka", "fr", "ga" and "em" (Emoji))

    NOTES:

    * "i18n.yaml" uses "...<" to indicate this, also in "behave/i18n.py".
    * Use "gherkin-languages.json" notation and adapt parser, etc. accordingly.
    * IMPACT: Step keywords may have an optional, trailing space character ?!?

* "scenarioOutline" ("gherkin-languages.json") vs. "scenario_outline" ("i18n.yml")
* "name", "native" are strings ("gherkin-languages.json") vs. array-of-string ("i18n.yml")
* NEW: "rule" (since: Gherkin v6)


Schema: "gherkin-languages.json"
-----------------------------------------------------------------------------

Schema description (JSON)::

    name    : string
    native  : string

    background  : sequence<string>
    feature     : sequence<string>
    rule        : sequence<string>
    scenario    : sequence<string>
    scenarioOutline : sequence<string>
    examples    : sequence<string>

    and     : sequence<string>
    but     : sequence<string>
    given   : sequence<string>
    when    : sequence<string>
    then    : sequence<string>


Schema example (JSON):

.. code-block:: json

  "en": {
    "name": "English",
    "native": "English",

    "feature": ["Feature", "Business Need", "Ability"],
    "rule": ["Rule"],
    "scenario": ["Example", "Scenario"],
    "scenarioOutline": ["Scenario Outline", "Scenario Template"],
    "background": ["Background"],
    "examples": ["Examples", "Scenarios"],

    "and": ["* ", "And "],
    "but": ["* ", "But "],
    "given": ["* ", "Given "],
    "when": ["* ", "When "]
    "then": ["* ", "Then "],
  },


Schema: "i18n.yml"
-----------------------------------------------------------------------------

Schema example (YAML):

.. code-block:: yaml

    "en":       # -- Language ID
        name: English
        native: English
        feature: Feature
        background: Background
        scenario: Scenario
        scenario_outline: Scenario Outline|Scenario Template
        examples: Examples|Scenarios
        given: "*|Given"
        when: "*|When"
        then: "*|Then"
        and: "*|And"
        but: "*|But"

Notes:

* Step keywords need split with "|" (pipe) into list.
