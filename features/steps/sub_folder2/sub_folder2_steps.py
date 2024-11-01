from behave import when

@when('a step is implemented in another sub folder')
def step_impl(context):
    context.nested_sub_folder2_visited = True
