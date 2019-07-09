Gherkin v6 Examples
=============================================================================


Provides example(s) of Gherkin v6 additions:

* Rule concept
* New aliases for Gherkin keywords (Scenario, ScenarioOutline)

Rule functionality:

* A Rule is a scenario container similar to a Feature
* A Feature may contain many Rules
* A Rule may not contain other Rules
* A Rule may contain a Background (and inherits its Feature Background)
* A Rule inherits its Feature Background if it has no Background
* A Rule may contain many Scenarios and/or ScenarioOutlines
* A Rule may have tags

New keyword aliases:

* "Scenario Template" for "Scenario Outline"
* "Example" for "Scenario"
