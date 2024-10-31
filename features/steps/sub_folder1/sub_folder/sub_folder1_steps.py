from behave import when

@when('a step is implemented in a sub-sub folder')
def step_impl(context):
    context.nested_sub_folder1_sub_folder_visited = True
