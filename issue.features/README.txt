issue.features:
===============================================================================

:Status:   PREPARED (fixes are being applied).
:Requires: Python >= 2.6 (due to step implementations)

This directory contains behave self-tests to ensure that behave related
issues are fixed.

PROCEDURE:

    * ONCE: Install python requirements ("requirements.txt")
    * Run the tests with behave

::

    bin/behave -f progress issue.features/
