.. _id.appendix.parse_expressions:

==============================================================================
Parse Expressions
==============================================================================

.. index:: parse expressions, regexp

`Parse expressions`_ are a simplified form of regular expressions.
The actual regular expression is hidden behind the **type** name / hint.

`Parse expressions`_ are used in step definitions as a simplified alternative
to regular expressions. They are used for parameters and type conversions
(which are not supported for regular expression patterns).

.. code-block:: python

    # -- FILE: features/steps/example_steps.py
    from behave import when

    @when('we implement {number:d} tests')
    def step_impl(context, number):  # -- NOTE: number is converted into integer
        assert number > 1 or number == 0
        context.tests_count = number

The following tables provide a overview of the `parse expressions`_ syntax.
See also `Python regular expressions`_ description in the Python `re module`_.

===== =========================================== ========
Type  Characters Matched                          Output
===== =========================================== ========
l     Letters (ASCII)                             str
w     Letters, numbers and underscore             str
W     Not letters, numbers and underscore         str
s     Whitespace                                  str
S     Non-whitespace                              str
d     Digits (effectively integer numbers)        int
D     Non-digit                                   str
n     Numbers with thousands separators (, or .)  int
%     Percentage (converted to value/100.0)       float
f     Fixed-point numbers                         float
F     Decimal numbers                             Decimal
e     Floating-point numbers with exponent        float
      e.g. 1.1e-10, NAN (all case insensitive)
g     General number format (either d, f or e)    float
b     Binary numbers                              int
o     Octal numbers                               int
x     Hexadecimal numbers (lower and upper case)  int
ti    ISO 8601 format date/time                   datetime
      e.g. 1972-01-20T10:21:36Z ("T" and "Z"
      optional)
te    RFC2822 e-mail format date/time             datetime
      e.g. Mon, 20 Jan 1972 10:21:36 +1000
tg    Global (day/month) format date/time         datetime
      e.g. 20/1/1972 10:21:36 AM +1:00
ta    US (month/day) format date/time             datetime
      e.g. 1/20/1972 10:21:36 PM +10:30
tc    ctime() format date/time                    datetime
      e.g. Sun Sep 16 01:03:52 1973
th    HTTP log format date/time                   datetime
      e.g. 21/Nov/2011:00:07:11 +0000
ts    Linux system log format date/time           datetime
      e.g. Nov  9 03:37:44
tt    Time                                        time
      e.g. 10:21:36 PM -5:30
===== =========================================== ========

If `parse_type`_ module is used, the cardinality of a type can be specified, too
(by using the `CardinalityField`_ support):

=====================  ==============================================================
Cardinality            Description
=====================  ==============================================================
``?``                   Pattern with cardinality 0..1: optional part (question mark).
``*``                   Pattern with cardinality zero or more, 0.. (asterisk).
``+``                   Pattern with cardinality one or more, 1.. (plus sign).
=====================  ==============================================================


.. _parse module: https://github.com/r1chardj0n3s/parse
.. _parse_type: https://github.com/jenisys/parse_type
.. _string.format: https://docs.python.org/3/library/string.html#format-string-syntax
.. _CardinalityField: https://github.com/jenisys/parse_type/blob/master/README.rst#extended-parser-with-cardinalityfield-support

.. _re module: https://docs.python.org/3/library/re.html#module-re
.. _Python regular expressions: https://docs.python.org/3/library/re.html#module-re
.. _`regular expressions`: https://en.wikipedia.org/wiki/Regular_expression

