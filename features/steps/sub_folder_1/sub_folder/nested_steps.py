from behave import given, then


@given('a general step is executed')
def step_impl(context):
    context.general_step_executed = True


@then('the general step should be recognized')
def step_impl(context):
    assert context.general_step_executed is True


