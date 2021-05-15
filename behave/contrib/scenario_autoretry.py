# -*- coding: UTF -*-
# pylint: disable=line-too-long
"""
Provides support functionality to retry scenarios a number of times before
their failure is accepted. This functionality can be helpful when you use
behave tests in a unreliable server/network infrastructure.

EXAMPLE:

.. sourcecode:: gherkin

    # -- FILE: features/alice.feature
    # TAG:  Feature or Scenario/ScenarioOutline with @autoretry
    # NOTE: If you tag the feature, all its scenarios are retried.
    @autoretry
    Feature: Use unreliable Server infrastructure

        Scenario: ...


.. sourcecode:: python

    # -- FILE: features/environment.py
    from behave.contrib.scenario_autoretry import patch_scenario_with_autoretry

    def before_feature(context, feature):
        for scenario in feature.walk_scenarios():
            if "autoretry" in scenario.effective_tags:
                patch_scenario_with_autoretry(scenario, max_attempts=2)

.. seealso::
    * https://github.com/behave/behave/pull/328
    * https://github.com/hypothesis/smokey/blob/sauce-reliability/smokey/features/environment.py
"""

from __future__ import print_function
import functools
from behave.model import ScenarioOutline
from time import sleep


def patch_scenario_with_autoretry(scenario, max_attempts=3, delay=0, backoff=1):
    """Monkey-patches :func:`~behave.model.Scenario.run()` to auto-retry a
    scenario that fails. The scenario is retried a number of times
    before its failure is accepted.

    This is helpful when the test infrastructure (server/network environment)
    is unreliable (which should be a rare case).

    :param scenario:        Scenario or ScenarioOutline to patch.
    :param max_attempts:    How many times the scenario can be run.
    :param delay:           Time to wait between scenario retries.
    :param backoff:         Backoff factor to increase the delay per retry.
    """
    def scenario_run_with_retries(scenario_run, *args, **kwargs):
        _delay = delay
        delay_message = ""
        for attempt in range(1, max_attempts+1):
            if not scenario_run(*args, **kwargs):
                if attempt > 1:
                    message = u"AUTO-RETRY SCENARIO PASSED (after {0} attempts)"
                    print(message.format(attempt))
                return False    # -- NOT-FAILED = PASSED

            # -- SCENARIO FAILED:
            if attempt < max_attempts:
                if delay:
                    if attempt > 1: _delay *= backoff
                    delay_message =  u" Delaying retry for {0}s".format(_delay)

                print(u"AUTO-RETRY SCENARIO (attempt {0}){1}".format(attempt, delay_message))
                sleep(_delay)

        message = u"AUTO-RETRY SCENARIO FAILED (after {0} attempts)"
        print(message.format(max_attempts))
        return True

    if isinstance(scenario, ScenarioOutline):
        scenario_outline = scenario
        for scenario in scenario_outline.scenarios:
            scenario_run = scenario.run
            scenario.run = functools.partial(scenario_run_with_retries, scenario_run)
    else:
        scenario_run = scenario.run
        scenario.run = functools.partial(scenario_run_with_retries, scenario_run)
