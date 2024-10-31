from behave import when

@when('a step module with an identical name exists in a sub folder')
def step_impl(context):
    context.nested_step_module_in_sub_folder1_visited = True
