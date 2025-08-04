from typing import List
from behave import when, then
from behave.cucumber_expression import (
    TypeBuilder,
    define_parameter_type_with
)
from example4me.color import Color
from assertpy import assert_that

parse_color = TypeBuilder.make_enum(Color)
parse_colors = TypeBuilder.with_many(parse_color)

# -- REGISTER PARAMETER TYPES:
define_parameter_type_with(
    name="colors",
    regexp=parse_colors.pattern,
    type=list,  # HINT: List[Color]
    transformer=parse_colors
)

# -- STEP DEFINITIONS: With OPTIONAL parts.
@when('I select the "{colors}" colo(u)r(s)')
def step_when_select_many_colors(ctx, colors: List[Color]):
    assert isinstance(colors, list)
    for index, color in enumerate(colors):
        assert isinstance(color, Color), "%r (index=%d)" % (color, index)
    ctx.selected_colors = colors

@then('I have selected {int} colo(u)r(s)')
def step_then_count_selected_colors(ctx, number_of_colors: int):
    assert isinstance(number_of_colors, int)
    assert_that(ctx.selected_colors).is_length(number_of_colors)
