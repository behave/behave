from behave import when

@when('a step module with an identical name exists in the sub-folder two levels deeper')
def step_impl(context):
    context.nested_sub_folder3_visited = True
