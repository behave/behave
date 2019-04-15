from behave import given, when, then

@given('something')
@then('nothing')
def step_none(context):
    pass


@then('I see the resource')
def see_resource(context):
    print("Resource is %r" % context.resource)

