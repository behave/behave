from behave.textutil import indent


# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------
NO_CAPTURED_OUTPUT =  "__HINT: NO_CAPTURED_OUTPUT"


# -----------------------------------------------------------------------------
# TEST SUPPORT: Print contents of captured output
# -----------------------------------------------------------------------------
def print_feature_captured_output(feature, prefix="  "):
    feature_output = feature.captured.make_output()
    feature_output = feature_output or NO_CAPTURED_OUTPUT
    print("FEATURE CAPTURED OUTPUT: {}\n{};\n".format(
        feature.name, indent(feature_output, prefix))
    )
    # -- ASSUMPTION: No rules exist.
    for scenario in feature.walk_scenarios():
        print_scenario_captured_output(scenario)


def print_rule_captured_output(rule, prefix="  "):
    rule_output = rule.captured.make_simple_report()
    rule_output = rule_output or NO_CAPTURED_OUTPUT
    print("RULE CAPTURED OUTPUT: {}\n{};\n".format(
        rule.name, indent(rule_output, prefix))
    )
    for scenario in rule.walk_scenarios():
        print_scenario_captured_output(scenario)


def print_scenario_captured_output(scenario, prefix="  "):
    scenario_output = scenario.captured.make_simple_report()
    scenario_output = scenario_output or NO_CAPTURED_OUTPUT
    print("SCENARIO CAPTURED OUTPUT: {}\n{};\n".format(
        scenario.name, indent(scenario_output, prefix))
    )
    for index, step in enumerate(scenario.steps):
        step_line = "{} {}".format(step.type.title(), step.name)
        step_output = step.captured.make_simple_report()
        if not step_output:
            step_output = NO_CAPTURED_OUTPUT
        print("STEP_{} CAPTURED OUTPUT: {}\n{};\n".format(
            index + 1, step_line, indent(step_output, prefix))
        )
        if step.error_message:
            print("STEP_{}.error_message:\n{};\n".format(
                index + 1, indent(step.error_message, prefix))
            )
