Noteworthy in Version 1.2.7
==============================================================================

Summary:

* Use/Support `cucumber-tag-expressions`_ (superceed: old-style tag-expressions)

* `cucumber-tag-expressions`_ are extended by "tag-matching"
  to match partial tag names, like: ``@foo.*``



.. _`cucumber-tag-expressions`: https://pypi.org/project/cucumber-tag-expressions/


New Tag-Expressions
-------------------------------------------------------------------------------

`cucumber-tag-expressions`_ are now supported and will superceed old-style
tag-expressions (which are deprecating). `cucumber-tag-expressions`_ are much
more readible and flexible to select tags on command-line.

.. code-block:: sh

    # -- SIMPLE TAG-EXPRESSION EXAMPLES:
    @a and @b
    @a or  @b
    not @a

    # -- MORE TAG-EXPRESSION EXAMPLES:
    @a and not @b
    (@a or @b) and not @c


.. seealso::

    * https://docs.cucumber.io/cucumber/api/#tag-expressions
