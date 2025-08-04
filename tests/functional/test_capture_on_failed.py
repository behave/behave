"""
Tests to verify that the capture output mechanisms works.
if the TEST ASSUMPTION, that is used here, is true.

* TEST ASSUMPTION: STORE_CAPTURED_ON_SUCCESS is False (only failures are captured)
"""

from mock import Mock
import pytest

from behave.configuration import Configuration
from behave.model_type import Status
from behave.parser import parse_feature, parse_rule, parse_scenario
from behave.runner import Context, ModelRunner

from tests.functional.capture_steps import load_steps_into_step_registry
from tests.functional.capture_util import (
    print_feature_captured_output,
    print_rule_captured_output,
    print_scenario_captured_output
)
from tests.functional.hooks import (
    good_before_feature, good_after_feature, good_before_rule, good_after_rule,
    good_before_scenario, good_after_scenario,
    bad_after_scenario_error, bad_before_scenario_failed,
    before_any_tag, after_any_tag
)


# ----------------------------------------------------------------------------
# TEST SUPPORT -- OTHER
# ----------------------------------------------------------------------------
def make_runner(hooks=None, **config_data):
    for param_name in ("capture", "capture_hooks"):
        if param_name not in config_data:
            config_data[param_name] = True
    if "verbose" not in config_data:
        config_data["verbose"] = False

    hooks = hooks or {}
    config = Configuration(load_config=False, **config_data)
    runner = ModelRunner(config)
    runner.context = Context(runner)
    runner.aborted = False
    runner.feature = Mock()
    runner.feature.tags = []
    runner.formatters = [Mock()]
    runner.hooks = hooks
    return runner


def make_runner_with_loaded_steps(hooks=None, **config_data):
    runner = make_runner(hooks, **config_data)
    runner.step_registry = load_steps_into_step_registry()
    return runner


# ----------------------------------------------------------------------------
# TEST SUPPORT: Fixtures
# ----------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def ensure_that_capture_sink_store_captured_on_success_is_false(monkeypatch):
    """All tests in this module require:

    * BasicStatement.STORE_CAPTURED_ON_SUCCESS is False
      (behave.model_core.BasicStatement)
    """
    # -- DERIVED FROM:
    # behave.constant.CAPTURE_SINK_STORE_CAPTURED_ON_SUCCESS = True
    from behave.model_core import BasicStatement
    monkeypatch.setattr(BasicStatement, "STORE_CAPTURED_ON_SUCCESS", False)


def require_store_captured_on_success_is_false():
    from behave.model_core import BasicStatement
    assert BasicStatement.STORE_CAPTURED_ON_SUCCESS is False


# ----------------------------------------------------------------------------
# TEST SUITE
# ----------------------------------------------------------------------------
class TestCaptureOnStepsRun(object):
    """Some additional tests for "Scenario.run()" using pytest."""

    def test_captured_with_passing_steps(self):
        require_store_captured_on_success_is_false()
        scenario_text = u"""
            Scenario: S1
              Given step1 passes with output
              When step2 passes with output
        """
        scenario = parse_scenario(scenario_text)

        # -- WHEN: I run the scenario
        runner = make_runner_with_loaded_steps()
        scenario.run(runner)
        assert scenario.steps[0].status == Status.passed
        assert scenario.steps[1].status == Status.passed
        assert scenario.status == Status.passed

        scenario_captured = scenario.captured
        step1_captured = scenario.steps[0].captured
        step2_captured = scenario.steps[1].captured
        scenario_output = scenario_captured.make_simple_report()
        step1_output = step1_captured.make_simple_report()
        step2_output = step2_captured.make_simple_report()
        print_scenario_captured_output(scenario)

        # -- THEN: I check the captured output
        assert step1_output == u""
        assert step2_output == u""
        assert scenario_output == u""
        # NOT: expected = u"CALLED: step1\nCALLED: step2\n"


    @pytest.mark.parametrize("failed_status", [Status.error, Status.failed])
    def test_failed_step_causes_remaining_steps_to_be_skipped(self, failed_status):
        require_store_captured_on_success_is_false()
        scenario_text = u"""
            Scenario: Fails in step2
              Given step1 passes with output
              When step2 fails with {failed_status.name}
              Then step3 passes with output
        """.format(failed_status=failed_status)
        scenario = parse_scenario(scenario_text)

        # -- WHEN: I run the scenario
        runner = make_runner_with_loaded_steps()
        run_scenario_failed = scenario.run(runner)
        print_scenario_captured_output(scenario)
        assert scenario.steps[0].status == Status.passed
        assert scenario.steps[1].status == failed_status
        assert scenario.steps[2].status == Status.skipped
        assert scenario.status == failed_status
        assert run_scenario_failed is True

        step1_captured = scenario.steps[0].captured
        step2_captured = scenario.steps[1].captured
        step3_captured = scenario.steps[2].captured
        step2 = scenario.steps[1]

        scenario_expected = u"""
CAPTURED STDOUT: scenario
CALLED: step1
BAD_CALLED: step2
""".strip()
        step2_expected = u"""
CAPTURED STDOUT: step
BAD_CALLED: step2

CAPTURED STDERR: step
ERROR: SomeError: OOPS, FAILED in step2
""".strip()
        if failed_status == Status.failed:
            scenario_expected = scenario_expected.replace("ERROR: SomeError:", "ASSERT FAILED:")
            step2_expected = step2_expected.replace("ERROR: SomeError:", "ASSERT FAILED:")

        assert step1_captured.stdout == u""  # -- GOOD_STEP: NO_OUTPUT
        assert step2_expected in step2_captured.make_simple_report()
        assert step3_captured.stdout == u""  # -- SKIPPED
        assert scenario.captured.make_simple_report() == scenario_expected
        assert "OOPS, FAILED in step2" in step2.error_message


class TestCaptureOnScenarioRun(object):

    def test_captured__good_steps_hooks_and_tags(self):
        require_store_captured_on_success_is_false()
        scenario_text = u"""
            @good_fixture.one
            @good_fixture.two
            Scenario: Good
              Given step1 passes with output
        """
        scenario = parse_scenario(scenario_text)

        # -- WHEN: I run the scenario
        runner = make_runner_with_loaded_steps()
        runner.hooks = dict(
            before_scenario=good_before_scenario,
            before_tag=before_any_tag,
            after_scenario=good_after_scenario,
        )
        run_scenario_failed = scenario.run(runner)
        print_scenario_captured_output(scenario)

        # -- THEN: I check the scenario/step status
        assert scenario.steps[0].status == Status.passed
        assert scenario.status == Status.passed
        assert run_scenario_failed is False

        # -- THEN: I check the captured outputs
        scenario_output = scenario.captured.make_simple_report()
        assert scenario_output == u""
        assert scenario.steps[0].captured.output == u""

    def test_captured__good_hooks_tags_with_bad_step(self):
        require_store_captured_on_success_is_false()
        scenario_text = u"""
            @good_fixture.one
            @good_fixture.two
            Scenario: Bad Step
              Given step1 passes with output
              When step2 fails with failed
              Then step3 passes with output
        """
        scenario = parse_scenario(scenario_text)

        # -- WHEN: I run the scenario
        runner = make_runner_with_loaded_steps()
        runner.hooks = dict(
            before_scenario=good_before_scenario,
            before_tag=before_any_tag,
            after_scenario=good_after_scenario,
        )
        run_scenario_failed = scenario.run(runner)
        print_scenario_captured_output(scenario)
        assert scenario.steps[0].status == Status.passed
        assert scenario.steps[1].status == Status.failed
        assert scenario.steps[2].status == Status.skipped
        assert scenario.status == Status.failed
        assert run_scenario_failed is True

        # -- THEN: I check the captured output
        step1_captured = scenario.steps[0].captured
        step2_captured = scenario.steps[1].captured
        step3_captured = scenario.steps[2].captured
        scenario_expected = u"""
CAPTURED STDOUT: scenario
CALLED: step1
BAD_CALLED: step2
""".strip()
        step2_expected = u"""
CAPTURED STDOUT: step
BAD_CALLED: step2

CAPTURED STDERR: step
ASSERT FAILED: OOPS, FAILED in step2
""".strip()
        assert step1_captured.make_simple_report() == u""
        assert step2_captured.make_simple_report() == step2_expected
        assert step3_captured.make_simple_report() == u""
        assert scenario.captured.make_simple_report() == scenario_expected

    def test_captured__bad_before_hook_and_good_steps(self):
        require_store_captured_on_success_is_false()
        scenario_text = u"""
            Scenario: Bad before-hook
              Given step1 passes with output
        """
        scenario = parse_scenario(scenario_text)

        # -- WHEN: I run the scenario
        runner = make_runner_with_loaded_steps()
        runner.hooks = dict(
            before_scenario=bad_before_scenario_failed,
            after_scenario=good_after_scenario,
        )
        run_scenario_failed = scenario.run(runner)
        print_scenario_captured_output(scenario)
        assert scenario.steps[0].status == Status.untested
        assert scenario.status == Status.hook_error
        assert run_scenario_failed is True

        # -- THEN: I check the captured output
        scenario_expected = u"""
CAPTURED STDOUT: before_scenario
BAD-HOOK: Bad before-hook -- before_scenario
HOOK-ERROR in before_scenario: AssertionError: OOPS, FAILED in Bad before-hook
""".strip()

        marker1 = u"HOOK-ERROR in before_scenario"
        marker2 = u"AssertionError: OOPS, FAILED in Bad before-hook"
        scenario_output = scenario.captured.make_simple_report()
        assert marker1 in scenario_output
        assert marker2 in scenario_output
        assert scenario_output == scenario_expected

    def test_captured__bad_after_hook_and_good_steps(self):
        require_store_captured_on_success_is_false()
        scenario_text = u"""
            Scenario: Bad after-hook
              Given step1 passes with output
        """
        scenario = parse_scenario(scenario_text)

        # -- WHEN: I run the scenario
        runner = make_runner_with_loaded_steps()
        runner.hooks = dict(
            before_scenario=good_before_scenario,
            after_scenario=bad_after_scenario_error,
        )
        run_scenario_failed = scenario.run(runner)
        print_scenario_captured_output(scenario)
        assert scenario.steps[0].status == Status.passed
        assert scenario.status == Status.hook_error
        assert run_scenario_failed is True

        # -- THEN: I check the captured output
        scenario_expected = u"""
CAPTURED STDOUT: after_scenario
BAD-HOOK: Bad after-hook -- after_scenario
HOOK-ERROR in after_scenario: SomeError: OOPS, ERROR in Bad after-hook
----
CAPTURED STDOUT: scenario
CALLED: step1
""".strip()
        _step1_expected = u"""
CAPTURED STDOUT: step
CALLED: step1
""".strip()
        marker1 = u"HOOK-ERROR in after_scenario"
        marker2 = u"SomeError: OOPS, ERROR in Bad after-hook"
        scenario_output = scenario.captured.make_simple_report()
        assert marker1 in scenario_output
        assert marker2 in scenario_output
        assert scenario_output == scenario_expected

    def test_captured__bad_before_tag_and_good_hook_steps(self):
        require_store_captured_on_success_is_false()
        scenario_text = u"""
            @good_fixture.one
            @bad_fixture_setup.two
            Scenario: Bad fixture-setup
              Given step1 passes with output
        """
        scenario = parse_scenario(scenario_text)

        # -- WHEN: I run the scenario
        runner = make_runner_with_loaded_steps()
        runner.hooks = dict(
            before_tag=before_any_tag,
        )
        run_scenario_failed = scenario.run(runner)
        print_scenario_captured_output(scenario)
        assert scenario.steps[0].status == Status.untested
        assert scenario.status == Status.hook_error
        assert run_scenario_failed is True

        # -- THEN: I check the captured output
        scenario_expected = u"""
CAPTURED STDOUT: before_tag
FIXTURE-SETUP: good_fixture.one
BAD_FIXTURE-SETUP: bad_fixture_setup.two
FIXTURE-CLEANUP: bad_fixture_setup.two
HOOK-ERROR in before_tag(tag=bad_fixture_setup.two): SomeError: OOPS, ERROR in bad_fixture_setup.two
""".strip()
        marker1 = u"HOOK-ERROR in before_tag(tag=bad_fixture_setup.two)"
        marker2 = u"SomeError: OOPS, ERROR in bad_fixture_setup.two"
        scenario_output = scenario.captured.make_simple_report()
        assert marker1 in scenario_output
        assert marker2 in scenario_output
        assert scenario_output == scenario_expected

    def test_captured__bad_hook_and_cleanup(self):
        require_store_captured_on_success_is_false()
        scenario_text = u"""
            @bad_fixture_cleanup.two
            @bad_after_tag.three
            Scenario: Bad after-tag
              Given step1 passes with output
        """
        scenario = parse_scenario(scenario_text)

        # -- WHEN: I run the scenario
        runner = make_runner_with_loaded_steps()
        runner.hooks = dict(
            before_tag=before_any_tag,
            after_tag=after_any_tag,
            # DISABLED: before_scenario=good_before_scenario,
            # DISABLED: after_scenario=good_after_scenario,
        )
        run_scenario_failed = scenario.run(runner)
        print_scenario_captured_output(scenario)
        assert scenario.steps[0].status == Status.passed
        assert scenario.status == Status.hook_error
        assert run_scenario_failed is True

        # -- THEN: I check the captured output
        scenario_expected_1 = u"""
CAPTURED STDOUT: after_tag
BAD-HOOK: tag=bad_after_tag.three
HOOK-ERROR in after_tag(tag=bad_after_tag.three): SomeError: OOPS, ERROR in bad_after_tag.three
----
CAPTURED STDOUT: scenario.cleanup
BAD_FIXTURE-CLEANUP: bad_fixture_cleanup.two
CLEANUP-ERROR in cleanup_fixture: SomeError: OOPS, ERROR in bad_fixture_cleanup.two
Traceback (most recent call last):
""".strip()
        scenario_expected_2 = u"""
  raise SomeError("OOPS, ERROR in {}".format(name))
tests.functional.error.SomeError: OOPS, ERROR in bad_fixture_cleanup.two
----
CAPTURED STDOUT: scenario
CALLED: step1
""".strip()
        marker1 = u"CLEANUP-ERROR in cleanup_fixture:"
        marker2 = u"SomeError: OOPS, ERROR in bad_fixture_cleanup.two"
        scenario_output = scenario.captured.make_simple_report()
        assert marker1 in scenario_output
        assert marker2 in scenario_output
        assert scenario_expected_1 in scenario_output
        assert scenario_expected_2 in scenario_output

    def test_captured__bad_cleanup_and_good_hook_steps(self):
        require_store_captured_on_success_is_false()
        scenario_text = u"""
            @good_fixture.one
            @bad_fixture_cleanup.two
            Scenario: Bad fixture-cleanup
              Given step1 passes with output
        """
        scenario = parse_scenario(scenario_text)

        # -- WHEN: I run the scenario
        runner = make_runner_with_loaded_steps()
        runner.hooks = dict(
            before_tag=before_any_tag,
            after_tag=after_any_tag,
        )
        run_scenario_failed = scenario.run(runner)
        print_scenario_captured_output(scenario)
        assert scenario.steps[0].status == Status.passed
        assert scenario.status == Status.cleanup_error
        assert run_scenario_failed is True

        # -- THEN: I check the captured output
        scenario_expected_1 = u"""
CAPTURED STDOUT: scenario.cleanup
BAD_FIXTURE-CLEANUP: bad_fixture_cleanup.two
CLEANUP-ERROR in cleanup_fixture: SomeError: OOPS, ERROR in bad_fixture_cleanup.two
Traceback (most recent call last):
""".strip()
        scenario_expected_2 = u"""
  raise SomeError("OOPS, ERROR in {}".format(name))
tests.functional.error.SomeError: OOPS, ERROR in bad_fixture_cleanup.two
FIXTURE-CLEANUP: good_fixture.one
----
CAPTURED STDOUT: scenario
CALLED: step1
""".strip()
        marker1 = u"CLEANUP-ERROR in cleanup_fixture:"
        marker2 = u"SomeError: OOPS, ERROR in bad_fixture_cleanup.two"
        scenario_output = scenario.captured.make_simple_report()
        assert marker1 in scenario_output
        assert marker2 in scenario_output
        assert scenario_output.startswith(scenario_expected_1)
        assert scenario_output.endswith(scenario_expected_2)


class TestCaptureOnRuleRun(object):

    def test_captured__good_hooks_tags_steps(self):
        require_store_captured_on_success_is_false()
        rule_text = u"""
            @good_fixture.one
            @good_fixture.two
            Rule: Good
              Scenario: Good S1
                Given step1 passes with output
        """
        rule = parse_rule(rule_text)

        # -- WHEN: I run the scenario
        runner = make_runner_with_loaded_steps()
        runner.hooks = dict(
            before_rule=good_before_rule,
            before_tag=before_any_tag,
            after_rule=good_after_rule,
        )
        run_rule_failed = rule.run(runner)
        print_rule_captured_output(rule)

        # -- THEN: I check the status
        scenario = rule.scenarios[0]
        assert rule.status == Status.passed
        assert scenario.status == Status.passed
        assert scenario.steps[0].status == Status.passed
        assert run_rule_failed is False

        # -- THEN: I check the captured output
        assert rule.captured.make_simple_report() == u""

    def test_captured__bad_cleanup_and_good_hooks_steps(self):
        require_store_captured_on_success_is_false()
        rule_text = u"""
            @good_fixture.one
            @bad_fixture_cleanup.two
            @good_fixture.three
            Rule: Bad fixture-cleanup
              Scenario: Good S1
                Given step1 passes with output
        """
        rule = parse_rule(rule_text)

        # -- WHEN: I run the scenario
        runner = make_runner_with_loaded_steps()
        runner.hooks = dict(
            before_tag=before_any_tag,
        )
        run_rule_failed = rule.run(runner)
        print_rule_captured_output(rule)
        scenario = rule.scenarios[0]
        assert rule.status == Status.cleanup_error
        assert scenario.status == Status.passed
        assert run_rule_failed is True

        rule_expected_1 = u"""
CAPTURED STDOUT: rule.cleanup
FIXTURE-CLEANUP: good_fixture.three
BAD_FIXTURE-CLEANUP: bad_fixture_cleanup.two
CLEANUP-ERROR in cleanup_fixture: SomeError: OOPS, ERROR in bad_fixture_cleanup.two
Traceback (most recent call last):
""".strip()
        rule_expected_2 = u"""
  raise SomeError("OOPS, ERROR in {}".format(name))
tests.functional.error.SomeError: OOPS, ERROR in bad_fixture_cleanup.two
FIXTURE-CLEANUP: good_fixture.one
""".strip()
        rule_output = rule.captured.make_simple_report()
        marker1 = u"CLEANUP-ERROR in cleanup_fixture"
        marker2 = u"SomeError: OOPS, ERROR in bad_fixture_cleanup.two"
        assert marker1 in rule_output
        assert marker2 in rule_output
        assert rule_output.startswith(rule_expected_1)
        assert rule_output.endswith(rule_expected_2)

    def test_captured__bad_after_tag_and_good_hooks_steps(self):
        require_store_captured_on_success_is_false()
        rule_text = u"""
            @good_fixture.one
            @bad_after_tag.two
            Rule: Bad after-tag
              Scenario: Good S1
                Given step1 passes with output
        """
        rule = parse_rule(rule_text)

        # -- WHEN: I run the scenario
        runner = make_runner_with_loaded_steps()
        runner.hooks = dict(
            before_tag=before_any_tag,
            after_tag=after_any_tag,
        )
        run_rule_failed = rule.run(runner)
        print_rule_captured_output(rule)

        # -- THEN: I check the status
        scenario = rule.scenarios[0]
        assert rule.status == Status.hook_error
        assert scenario.status == Status.passed
        assert run_rule_failed is True

        # -- THEN: I check the captured output
        rule_expected = u"""
CAPTURED STDOUT: after_tag
BAD-HOOK: tag=bad_after_tag.two
HOOK-ERROR in after_tag(tag=bad_after_tag.two): SomeError: OOPS, ERROR in bad_after_tag.two
""".strip()
        rule_output = rule.captured.make_simple_report()
        marker1 = u"HOOK-ERROR in after_tag(tag=bad_after_tag.two):"
        marker2 = u"SomeError: OOPS, ERROR in bad_after_tag.two"
        assert marker1 in rule_output
        assert marker2 in rule_output
        assert rule_output == rule_expected

    def test_captured__bad_cleanup_and_after_tag(self):
        require_store_captured_on_success_is_false()
        rule_text = u"""
            @bad_after_tag.one
            @bad_fixture_cleanup.two
            Rule: Bad after-tag
              Scenario: Good S1
                Given step1 passes with output
        """
        rule = parse_rule(rule_text)

        # -- WHEN: I run the scenario
        runner = make_runner_with_loaded_steps()
        runner.hooks = dict(
            before_tag=before_any_tag,
            after_tag=after_any_tag,
        )
        run_rule_failed = rule.run(runner)
        print_rule_captured_output(rule)
        scenario = rule.scenarios[0]
        assert rule.status == Status.hook_error
        assert scenario.status == Status.passed
        assert run_rule_failed is True

        rule_expected_1 = u"""
CAPTURED STDOUT: after_tag
BAD-HOOK: tag=bad_after_tag.one
HOOK-ERROR in after_tag(tag=bad_after_tag.one): SomeError: OOPS, ERROR in bad_after_tag.one
----
CAPTURED STDOUT: rule.cleanup
BAD_FIXTURE-CLEANUP: bad_fixture_cleanup.two
CLEANUP-ERROR in cleanup_fixture: SomeError: OOPS, ERROR in bad_fixture_cleanup.two
Traceback (most recent call last):
""".strip()
        rule_expected_2 = u"""
  raise SomeError("OOPS, ERROR in {}".format(name))
tests.functional.error.SomeError: OOPS, ERROR in bad_fixture_cleanup.two
""".strip()

        rule_output = rule.captured.make_simple_report()
        marker1 = u"HOOK-ERROR in after_tag(tag=bad_after_tag.one):"
        marker2 = u"SomeError: OOPS, ERROR in bad_after_tag.one"
        marker3 = u"CLEANUP-ERROR in cleanup_fixture:"
        marker4 = u"SomeError: OOPS, ERROR in bad_fixture_cleanup.two"
        assert marker1 in rule_output
        assert marker2 in rule_output
        assert marker3 in rule_output
        assert marker4 in rule_output
        assert rule_output.startswith(rule_expected_1)
        assert rule_output.endswith(rule_expected_2)


class TestCaptureOnFeatureRun(object):

    def test_captured__good_hooks_tags_steps(self):
        require_store_captured_on_success_is_false()
        feature_text = u"""
            @good_fixture.one
            @good_fixture.two
            Feature: Good
              Scenario: Good S1
                Given step1 passes with output
        """
        feature = parse_feature(feature_text)

        # -- WHEN: I run the scenario
        runner = make_runner_with_loaded_steps()
        runner.hooks = dict(
            before_feature=good_before_feature,
            before_tag=before_any_tag,
            after_feature=good_after_feature,
        )
        run_feature_failed = feature.run(runner)
        print_feature_captured_output(feature)
        scenario = feature.scenarios[0]
        assert feature.status == Status.passed
        assert scenario.status == Status.passed
        assert scenario.steps[0].status == Status.passed
        assert run_feature_failed is False

        # -- USING: STORE_CAPTURE_ON_SUCCESS=false -> NO_OUTPUT
        assert feature.captured.make_simple_report() == u""

    def test_captured__bad_cleanup_and_good_hooks_steps(self):
        require_store_captured_on_success_is_false()
        feature_text = u"""
            @good_fixture.one
            @bad_fixture_cleanup.two
            @good_fixture.three
            Feature: Bad fixture-cleanup
              Scenario: Good S1
                Given step1 passes with output
        """
        feature = parse_feature(feature_text)

        # -- WHEN: I run the scenario
        runner = make_runner_with_loaded_steps()
        runner.hooks = dict(
            before_tag=before_any_tag,
        )
        run_feature_failed = feature.run(runner)
        print_feature_captured_output(feature)
        scenario = feature.scenarios[0]
        assert feature.status == Status.cleanup_error
        assert scenario.status == Status.passed
        assert run_feature_failed is True

        feature_expected_1 = u"""
CAPTURED STDOUT: feature.cleanup
FIXTURE-CLEANUP: good_fixture.three
BAD_FIXTURE-CLEANUP: bad_fixture_cleanup.two
CLEANUP-ERROR in cleanup_fixture: SomeError: OOPS, ERROR in bad_fixture_cleanup.two
Traceback (most recent call last):
""".strip()
        feature_expected_2 = u"""
  raise SomeError("OOPS, ERROR in {}".format(name))
tests.functional.error.SomeError: OOPS, ERROR in bad_fixture_cleanup.two
FIXTURE-CLEANUP: good_fixture.one
""".strip()
        feature_output = feature.captured.make_simple_report()
        marker1 = u"CLEANUP-ERROR in cleanup_fixture"
        marker2 = u"SomeError: OOPS, ERROR in bad_fixture_cleanup.two"
        assert marker1 in feature_output
        assert marker2 in feature_output
        assert feature_output.startswith(feature_expected_1)
        assert feature_output.endswith(feature_expected_2)

    def test_captured__bad_after_tag_and_good_hooks_steps(self):
        require_store_captured_on_success_is_false()
        feature_text = u"""
            @good_fixture.one
            @bad_after_tag.two
            Feature: Bad after-tag
              Scenario: Good S1
                Given step1 passes with output
        """
        feature = parse_feature(feature_text)

        # -- WHEN: I run the scenario
        runner = make_runner_with_loaded_steps()
        runner.hooks = dict(
            before_tag=before_any_tag,
            after_tag=after_any_tag,
        )
        run_feature_failed = feature.run(runner)
        print_feature_captured_output(feature)

        # -- THEN: I check the status
        scenario = feature.scenarios[0]
        assert feature.status == Status.hook_error
        assert scenario.status == Status.passed
        assert run_feature_failed is True

        # -- THEN: I check the captured output
        feature_expected = u"""
CAPTURED STDOUT: after_tag
BAD-HOOK: tag=bad_after_tag.two
HOOK-ERROR in after_tag(tag=bad_after_tag.two): SomeError: OOPS, ERROR in bad_after_tag.two
""".strip()
        feature_output = feature.captured.make_simple_report()
        marker1 = u"HOOK-ERROR in after_tag(tag=bad_after_tag.two):"
        marker2 = u"SomeError: OOPS, ERROR in bad_after_tag.two"
        assert marker1 in feature_output
        assert marker2 in feature_output
        assert feature_output == feature_expected

    def test_captured__bad_cleanup_and_after_tag(self):
        require_store_captured_on_success_is_false()
        feature_text = u"""
            @bad_after_tag.one
            @bad_fixture_cleanup.two
            Feature: Bad after-tag
              Scenario: Good S1
                Given step1 passes with output
        """
        feature = parse_feature(feature_text)

        # -- WHEN: I run the scenario
        runner = make_runner_with_loaded_steps()
        runner.hooks = dict(
            before_tag=before_any_tag,
            after_tag=after_any_tag,
        )
        run_feature_failed = feature.run(runner)
        print_feature_captured_output(feature)
        scenario = feature.scenarios[0]
        assert feature.status == Status.hook_error
        assert scenario.status == Status.passed
        assert run_feature_failed is True

        feature_expected_1 = u"""
CAPTURED STDOUT: after_tag
BAD-HOOK: tag=bad_after_tag.one
HOOK-ERROR in after_tag(tag=bad_after_tag.one): SomeError: OOPS, ERROR in bad_after_tag.one
----
CAPTURED STDOUT: feature.cleanup
BAD_FIXTURE-CLEANUP: bad_fixture_cleanup.two
CLEANUP-ERROR in cleanup_fixture: SomeError: OOPS, ERROR in bad_fixture_cleanup.two
Traceback (most recent call last):
""".strip()
        feature_expected_2 = u"""
  raise SomeError("OOPS, ERROR in {}".format(name))
tests.functional.error.SomeError: OOPS, ERROR in bad_fixture_cleanup.two
""".strip()

        feature_output = feature.captured.make_simple_report()
        marker1 = u"HOOK-ERROR in after_tag(tag=bad_after_tag.one):"
        marker2 = u"SomeError: OOPS, ERROR in bad_after_tag.one"
        marker3 = u"CLEANUP-ERROR in cleanup_fixture:"
        marker4 = u"SomeError: OOPS, ERROR in bad_fixture_cleanup.two"
        assert marker1 in feature_output
        assert marker2 in feature_output
        assert marker3 in feature_output
        assert marker4 in feature_output
        assert feature_output.startswith(feature_expected_1)
        assert feature_output.endswith(feature_expected_2)
