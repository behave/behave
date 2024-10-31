from behave import when

@when('a step is implemented in a sub folder')
def step_impl(context):
    context.nested_sub_folder1_visited = True
