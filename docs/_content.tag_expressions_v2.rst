Tag-Expressions v2
-------------------------------------------------------------------------------

Tag-Expressions v2 are based on :pypi:`cucumber-tag-expressions` with some extensions:

* Tag-Expressions v2 provide `boolean logic expression`
  (with ``and``, ``or`` and ``not`` operators and parenthesis for grouping expressions)
* Tag-Expressions v2 are far more readable and composable than Tag-Expressions v1
* Some boolean-logic-expressions where not possible with Tag-Expressions v1
* Therefore, Tag-Expressions v2 supersedes the old-style tag-expressions.


.. code-block:: gherkin
    :caption: TAG-EXPRESSION EXAMPLES

    # -- EXAMPLE 1: Select features/scenarios that have the tags: @a and @b
    @a and @b

    # -- EXAMPLE 2: Select features/scenarios that have the tag: @a or @b
    @a or @b

    # -- EXAMPLE 3: Select features/scenarios that do not have the tag: @a
    not @a

    # -- EXAMPLE 4: Select features/scenarios that have the tags: @a but not @b
    @a and not @b

    # -- EXAMPLE 5: Select features/scenarios that have the tags: (@a or @b) but not @c
    # HINT: Boolean expressions can be grouped with parenthesis.
    (@a or @b) and not @c

COMMAND-LINE EXAMPLE:

.. code-block:: sh
    :caption: USING: Tag-Expressions v2 with ``behave``

    # -- SELECT-BY-TAG-EXPRESSION (with tag-expressions v2):
    # Select all features / scenarios with both "@foo" and "@bar" tags.
    $ behave --tags="@foo and @bar" features/

    # -- EXAMPLE: Use default_tags from config-file "behave.ini".
    # Use placeholder "{config.tags}" to refer to this tag-expression.
    # HERE: config.tags = "not (@xfail or @not_implemented)"
    $ behave --tags="(@foo or @bar) and {config.tags}" --tags-help
    ...
    CURRENT TAG_EXPRESSION: ((foo or bar) and not (xfail or not_implemented))

    # -- EXAMPLE: Uses Tag-Expression diagnostics with --tags-help option
    $ behave --tags="(@foo and @bar) or @baz" --tags-help
    $ behave --tags="(@foo and @bar) or @baz" --tags-help --verbose

.. seealso::

    * https://docs.cucumber.io/cucumber/api/#tag-expressions
    * :pypi:`cucumber-tag-expressions` (Python package)


Tag Matching with Tag-Expressions
-------------------------------------------------------------------------------

Tag-Expressions v2 support **partial string/tag matching** with wildcards.
This supports tag-expressions:

=================== =========== =========== ===================================================
Tag Matching Idiom  Example 1   Example 2   Description
=================== =========== =========== ===================================================
``tag.starts_with`` ``@foo.*``  ``foo.*``   Search for tags that start with a ``prefix``.
``tag.ends_with``   ``@*.one``  ``*.one``   Search for tags that end with a ``suffix``.
``tag.contains``    ``@*foo*``  ``*foo*``   Search for tags that contain a ``part``.
=================== =========== =========== ===================================================

.. code-block:: gherkin
    :caption: FILE: features/one.feature

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
    :caption: USAGE EXAMPLE: Run behave with tag-matching expressions

    $ behave -f plain --tags="@foo.*" features/one.feature
    Feature: Alice

      Scenario: Alice.1
        ...

      Scenario: Alice.2
        ...

    # -- HINT: Only Alice.1 and Alice.2 are matched (not: Alice.3).

.. note::

    * Filename matching wildcards are supported.
      See :mod:`fnmatch` (Unix style filename matching).

    * The tag matching functionality is an extension to :pypi:`cucumber-tag-expressions`.


Select the Tag-Expression Version to Use
-------------------------------------------------------------------------------

The tag-expression version, that should be used by :pypi:`behave`,
can be specified in the :pypi:`behave` config-file.

This allows a user to select:

* Tag-Expressions v1 (if needed)
* Tag-Expressions v2 when it is feasible

EXAMPLE:

.. code-block:: ini
    :caption: FILE: behave.ini

    # SPECIFY WHICH TAG-EXPRESSION-PROTOCOL SHOULD BE USED:
    #   SUPPORTED VALUES: v1, v2, auto_detect
    #   CURRENT DEFAULT:  auto_detect
    [behave]
    tag_expression_protocol = v1    # -- Use Tag-Expressions v1.


Tag-Expressions v1
-------------------------------------------------------------------------------

Tag-Expressions v1 are becoming deprecated (but are currently still supported).
Use **Tag-Expressions v2** instead.

.. note::

    Tag-Expressions v1 support will be dropped in ``behave v1.4.0``.
