from behave import when

@when('a step is implemented in another sub-sub folder with an identical name')
def step_impl(context):
    context.nested_sub_folder2_sub_folder_visited = True
