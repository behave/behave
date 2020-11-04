issue.features:
===============================================================================

:Requires: Python >= 2.7 or Python >= 3.5

This directory contains behave self-tests to ensure that behave related
issues are fixed.

PROCEDURE:

    * ONCE: Install python requirements ("py.requirements.txt")
    * Run the tests with behave

.. code-block:: shell

    # -- FOR:
    # pip:  For python2.7 or python3 (depends on platform and/or user))
    # pip3: For python3
    pip  install -U -r issue.features/testing.txt
    pip3 install -U -r issue.features/testing.txt


ALTERNATIVE:

.. code-block:: shell

    pip  install -U -r py.requirements/testing.txt
    pip3 install -U -r py.requirements/testing.txt

.. code-block:: shell

    bin/behave -f progress issue.features/
