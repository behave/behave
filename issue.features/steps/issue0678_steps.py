# issue #678: Support tags with commas and semicolons.
from behave import given, when, then


@given('I inspect the tags of the current scenario')
@when('I inspect the tags of the current scenario')
def step_inspect_scenario_tags(context):
    print("scenario.tags= %r" % context.scenario.tags)


@then('the tag "{tag}" is contained')
def check_tag(context, tag):
    assert tag in context.scenario.tags, "OOPS: tag={0} is missing".format(tag)
