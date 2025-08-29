from behave import given

@given('I meet "{person_name:w}"')
def step_impl(ctx, person_name: str):
    ctx.person_name = person_name

@given('I meet "{person_name:w} at the {location:w}"')
def step_impl(ctx, person_name: str, location: str):
    ctx.person_name = person_name
    ctx.location = location
