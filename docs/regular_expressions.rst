.. _id.appendix.regular_expressions:

==============================================================================
Regular Expressions
==============================================================================

.. index:: regular expressions, regexp

The following tables provide a overview of the `regular expressions`_ syntax.
See also `Python regular expressions`_ description in the Python `re module`_.


=====================  =========================================================
Special Characters      Description
=====================  =========================================================
``.``                   Matches any character (dot).
``^``                   "^...", matches start-of-string (caret).
``$``                   "...$", matches end-of-string (dollar sign).
``|``                   "A|B", matches "A" or "B".
``\``                   Escape character.
``\.``                  EXAMPLE: Matches character '.' (dot).
``\\``                  EXAMPLE: Matches character '``\``' (backslash).
=====================  =========================================================

To select or match characters from a special set of characters,
a character set must be defined.

=====================  =========================================================
Character sets          Description
=====================  =========================================================
``[...]``               Define a character set, like ``[A-Za-z]``.
``\d``                  Matches digit character: [0-9]
``\D``                  Matches non-digit character.
``\s``                  Matches whitespace character: ``[ \t\n\r\f\v]``
``\S``                  Matches non-whitespace character
``\w``                  Matches alphanumeric character: ``[a-zA-Z0-9_]``
``\W``                  Matches non-alphanumeric character.
=====================  =========================================================

A text part must be group to extract it as part (parameter).

=====================  =========================================================
Grouping                Description
=====================  =========================================================
``(...)``               Group a regular expression pattern (anonymous group).
``\number``             Matches text of earlier group by index, like: "``\1``".
``(?P<name>...)``       Matches pattern and stores it in parameter "name".
``(?P=name)``           Match whatever text was matched by earlier group "name".
``(?:...)``             Matches pattern, but does non capture any text.
``(?#...)``             Comment (is ignored), describes pattern details.
=====================  =========================================================

If a *group*, *character* or *character set* should be repeated several times,
it is necessary to specify the cardinality of the regular expression pattern.

=====================  ==============================================================
Cardinality            Description
=====================  ==============================================================
``?``                   Pattern with cardinality 0..1: optional part (question mark).
``*``                   Pattern with cardinality zero or more, 0.. (asterisk).
``+``                   Pattern with cardinality one or more, 1.. (plus sign).
``{m}``                 Matches ``m`` repetitions of a pattern.
``{m,n}``               Matches from ``m`` to ``n`` repetitions of a pattern.
``[A-Za-z]+``           EXAMPLE: Matches one or more alphabetical characters.
=====================  ==============================================================


.. _`regular expressions`: http://en.wikipedia.org/wiki/Regular_expression
.. _Python regular expressions: http://docs.python.org/2/library/re.html#module-re
.. _re module: http://docs.python.org/2/library/re.html#module-re




