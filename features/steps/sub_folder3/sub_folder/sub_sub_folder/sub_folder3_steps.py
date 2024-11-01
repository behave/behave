from behave import when

@when('a step is implemented in a sub-sub-sub folder with no module in the intermediate level')
def step_impl(context):
    context.nested_sub_sub_folder3_visited = True
