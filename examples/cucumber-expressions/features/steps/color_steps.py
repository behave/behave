# -- REQUIRES: Python3
from behave import when, then
from behave.cucumber_expression import (
    ParameterType,
    define_parameter_type,
    # -- SIMILAR-TO: define_parameter_type_with
)
from example4me.color import Color

# -- REGISTER PARAMETER TYPES:
# OR: Use define_parameter_type_with(name="color", ...)
define_parameter_type(ParameterType(
    name="color",
    regexp="red|green|blue",
    type=Color,
    transformer=Color.from_name
))

# -- STEP DEFINITIONS: With OPTIONAL parts.
@when('I select the "{color}" theme colo(u)r')
def step_when_select_color_theme(ctx, color: Color):
    assert isinstance(color, Color)
    ctx.selected_color = color

@then('the profile colo(u)r should be "{color}"')
def step_then_profile_color_should_be(ctx, the_color: Color):
    assert isinstance(the_color, Color)
    assert ctx.selected_color == the_color
