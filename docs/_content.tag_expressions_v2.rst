Tag-Expressions v2
-------------------------------------------------------------------------------

:pypi:`cucumber-tag-expressions` are now supported and superceed the old-style
tag-expressions (which are deprecating). :pypi:`cucumber-tag-expressions` are much
more readible and flexible to select tags on command-line.

.. code-block:: sh

    # -- SIMPLE TAG-EXPRESSION EXAMPLES:
    @a and @b
    @a or  @b
    not @a

    # -- MORE TAG-EXPRESSION EXAMPLES:
    # HINT: Boolean expressions can be grouped with parenthesis.
    @a and not @b
    (@a or @b) and not @c

Example:

.. code-block:: sh

    # -- SELECT-BY-TAG-EXPRESSION (with tag-expressions v2):
    # Sellect all features / scenarios with both "@foo" and "@bar" tags.
    $ behave --tags="@foo and @bar" features/


.. seealso::

    * https://docs.cucumber.io/cucumber/api/#tag-expressions


Tag Matching with Tag-Expressions
-------------------------------------------------------------------------------

The new tag-expressions also support **partial string/tag matching** with wildcards.

.. code-block:: gherkin

    # -- FILE: features/one.feature
    Feature: Alice

      @foo.one
      Scenario: Alice.1
        ...

      @foo.two
      Scenario: Alice.2
        ...

      @bar
      Scenario: Alice.3
        ...

The following command-line will select all features / scenarios with tags
that start with "@foo.":

.. code-block:: sh

    $ behave -f plain --tags="@foo.*" features/one.feature
    Feature: Alice

      Scenario: Alice.1
        ...

      Scenario: Alice.2
        ...

    # -- HINT: Only Alice.1 and Alice.2 are matched (not: Alice.3).

.. hint::

    * Filename matching wildcards are supported.
      See :mod:`fnmatch` (Unix style filename matching).

    * The tag matching functionality is an extension to :pypi:`cucumber-tag-expressions`.
