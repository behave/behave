from behave import given, when, then


class DinnerReservation:
    def __init__(self, person_name: str):
        self.name = person_name


@when('I invite "{person_name:w}" for dinner')
def step_impl(ctx, person_name: str):
    ctx.person_name = person_name
    ctx.dinner_reservation = DinnerReservation(person_name)

@then('a dinner reservation for "{person_name:w}" and me was made')
def step_impl(ctx, person_name: str):
    assert ctx.dinner_reservation is ctx.person_name
