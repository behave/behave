Noteworthy in Version 1.2.5
==============================================================================


.. index::
    single: ScenarioOutline; name annotation
    pair:   ScenarioOutline; file location

Scenario Outline: Better represent Example/Row
-------------------------------------------------------------------------------

:Since:  behave 1.2.5a1
:Covers: Name annotation, file location

A scenario outline basically a parametrized scenario template.
It represents a macro/script that is executed for a data-driven set of examples
(parametrized data). Therefore, a scenario outline generates several scenarios,
each representing one example/row combination.

.. code-block:: gherkin

    # -- file:features/xxx.feature
    Feature:
      Scenario Outline: Wow            # line 2
        Given an employee "<name>"

        Examples: Araxas
          | name  | birthyear |
          | Alice |  1985     |         # line 7
          | Bob   |  1975     |         # line 8

        Examples:
          | name   | birthyear |
          | Charly |  1995     |        # line 12


Up to now, the following scenarios were generated from the scenario outline:

.. code-block:: gherkin

    Scenario Outline: Wow          # features/xxx.feature:2
      Given an employee "Alice"

    Scenario Outline: Wow          # features/xxx.feature:2
      Given an employee "Bob"

    Scenario Outline: Wow          # features/xxx.feature:2
      Given an employee "Charly"

Note that  all generated scenarios had the:

  * same name (scenario_outline.name)
  * same file location (scenario_outline.file_location)

From now on, the generated scenarios better
represent the example/row combination within a scenario outline:

.. code-block:: gherkin

    Scenario Outline: Wow -- @1.1 Araxas  # features/xxx.feature:7
      Given an employee "Alice"

    Scenario Outline: Wow -- @1.2 Araxas  # features/xxx.feature:8
      Given an employee "Bob"

    Scenario Outline: Wow -- @2.1         # features/xxx.feature:12
      Given an employee "Charly"

Note that:

  * scenario name is now unique for any examples/row combination
  * scenario name optionally contains the examples (group) name (if one exists)
  * each scenario has a unique file location, based on the row's file location

Therefore, each generated scenario from a scenario outline can be selected
via its file location (and run on its own). In addition, if one fails,
it is now possible to rerun only the failing example/row combination(s).

The name annoations schema for the generated scenarios from above provides
the new default name annotation schema.
It can be adapted/overwritten in "behave.ini":

.. code-block:: ini

    # -- file:behave.ini
    [behave]
    scenario_outline_annotation_schema = {name} -- @{row.id} {examples.name}

    # -- REVERT TO: Old naming schema:
    # scenario_outline_annotation_schema = {name}


The following additional placeholders are provided within a
scenario outline to support this functionality.
They can be used anywhere within a scenario outline.

=============== ===============================================================
Placeholder     Description
=============== ===============================================================
examples.name   Refers name of the example group, may be an empty string.
examples.index  Index of the example group (range=1..N).
row.index       Index of the current row within an example group (range=1..R).
row.id          Shortcut for schema: "<examples.index>.<row.index>"
=============== ===============================================================


.. index::
    single: ScenarioOutline; name with placeholders

Scenario Outline: Name may contain Placeholders
-------------------------------------------------------------------------------

:Since: behave 1.2.5a1

A scenario outline can now use placeholders from example/rows in its name
or its examples name. When the scenarios a generated,
these placeholders will be replaced with the values of the example/row.

Up to now this behavior did only apply to steps of a scenario outline.

EXAMPLE:

.. code-block:: gherkin

    # -- file:features/xxx.feature
    Feature:
      Scenario Outline: Wow <name>-<birthyear>  # line 2
        Given an employee "<name>"

        Examples:
          | name  | birthyear |
          | Alice |  1985     |         # line 7
          | Bob   |  1975     |         # line 8

        Examples: Benares-<ID>
          | name   | birthyear | ID |
          | Charly |  1995     | 42 |   # line 12


This leads to the following generated scenarios,
one for each examples/row combination:

.. code-block:: gherkin

    Scenario Outline: Wow Alice-1985 -- @1.1         # features/xxx.feature:7
      Given an employee "Alice"

    Scenario Outline: Wow Bob-1975 -- @1.2           # features/xxx.feature:8
      Given an employee "Bob"

    Scenario Outline: Wow Charly-1885 -- @2.1 Benares-42 # features/xxx.feature:12
      Given an employee "Charly"

.. index::
    pair:   ScenarioOutline; tags with placeholders

Scenario Outline: Tags may contain Placeholders
-------------------------------------------------------------------------------

:Since: behave 1.2.5a1

Tags from a Scenario Outline are also part of the parametrized template.
Therefore, you may also use placeholders in the tags of a Scenario Outline.

.. note::

    * Placeholder names, that are used in tags, should not contain whitespace.
    * Placeholder values, that are used in tags, are transformed to contain
      no whitespace characters.


EXAMPLE:

.. code-block:: gherkin

    # -- file:features/xxx.feature
    Feature:

      @foo.group<examples.index>
      @foo.row<row.id>
      @foo.name.<name>
      Scenario Outline: Wow            # line 6
        Given an employee "<name>"

        Examples: Araxas
          | name  | birthyear |
          | Alice |  1985     |         # line 11
          | Bob   |  1975     |         # line 12

        Examples: Benares
          | name   | birthyear | ID |
          | Charly |  1995     | 42 |   # line 16


This leads to the following generated scenarios,
one for each examples/row combination:

.. code-block:: gherkin

    @foo.group1 @foo.row1.1 @foo.name.Alice
    Scenario Outline: Wow -- @1.1 Araxas   # features/xxx.feature:11
      Given an employee "Alice"

    @foo.group1 @foo.row1.2 @foo.name.Bob
    Scenario Outline: Wow -- @1.2 Araxas   # features/xxx.feature:12
      Given an employee "Bob"

    @foo.group2 @foo.row2.1 @foo.name.Charly
    Scenario Outline: Wow -- @2.1 Benares  # features/xxx.feature:16
      Given an employee "Charly"

.. index::
    single: ScenarioOutline; select-group-by-tag

It is now possible to run only the examples group "Araxas" (examples group 1)
by using the select-by-tag mechanism:

.. code-block:: sh

    $ behave --tags=@foo.group1 -f progress3 features/xxx.feature
    ...  # features/xxx.feature
      Wow -- @1.1 Araxas  .
      Wow -- @1.2 Araxas  .


.. index::
    single: ScenarioOutline; select-group-by-name

Scenario Outline: Run examples group via select-by-name
-------------------------------------------------------------------------------

:Since: behave 1.2.5a1

The improvements on unique generated scenario names for a scenario outline
(with name annotation) can now be used to run all rows of one examples group.

EXAMPLE:

.. code-block:: gherkin

    # -- file:features/xxx.feature
    Feature:
      Scenario Outline: Wow            # line 2
        Given an employee "<name>"

        Examples: Araxas
          | name  | birthyear |
          | Alice |  1985     |         # line 7
          | Bob   |  1975     |         # line 8

        Examples: Benares
          | name   | birthyear |
          | Charly |  1995     |        # line 12


This leads to the following generated scenarios (when the feature is executed):

.. code-block:: gherkin

    Scenario Outline: Wow -- @1.1 Araxas  # features/xxx.feature:7
      Given an employee "Alice"

    Scenario Outline: Wow -- @1.2 Araxas   # features/xxx.feature:8
      Given an employee "Bob"

    Scenario Outline: Wow -- @2.1 Benares  # features/xxx.feature:12
      Given an employee "Charly"


You can now run all rows of the "Araxas" examples (group)
by selecting it by name (name part or regular expression):

.. code-block:: sh

    $ behave --name=Araxas -f progress3 features/xxx.feature
    ...  # features/xxx.feature
      Wow -- @1.1 Araxas  .
      Wow -- @1.2 Araxas  .

    $ behave --name='-- @.* Araxas' -f progress3 features/xxx.feature
    ...  # features/xxx.feature
      Wow -- @1.1 Araxas  .
      Wow -- @1.2 Araxas  .
