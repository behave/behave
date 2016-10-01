EXAMPLE: Use Environment Variables in Steps
=============================================================================

:RELATED TO: `issue #497`_

This directory provides a simple example how you can use environment variables
in step implementations.

::

    # -- USE: -f plain --no-capture  (via "behave.ini" defaults)
    $ behave
    Feature: Test Environment variable concept

      Scenario: 
    USE ENVIRONMENT-VAR: LOGNAME = xxx  (variant 1)
        When I click on $LOGNAME ... passed
    USE ENVIRONMENT-VAR: LOGNAME = xxx  (variant 2)
        When I use the environment variable $LOGNAME ... passed

    1 feature passed, 0 failed, 0 skipped
    1 scenario passed, 0 failed, 0 skipped
    2 steps passed, 0 failed, 0 skipped, 0 undefined
    Took 0m0.000s

.. _`issue #497`: https://github.com/behave/behave/issues/497
