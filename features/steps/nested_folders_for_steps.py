# ruff: noqa: F811
from behave import then, when


@when('a step is implemented in the root folder')
def step_impl(context):
    context.nested_root_visited = True


@when('a step module with an identical name exists in the root folder')
def step_impl(context):
    context.nested_step_module_in_root_visited = True


@then('the implementation from all nested step modules has been executed')
def step_impl(context):
    assert context.nested_root_visited
    assert context.nested_sub_folder1_visited
    assert context.nested_sub_folder1_sub_folder_visited
    assert context.nested_sub_folder2_visited
    assert context.nested_sub_folder2_sub_folder_visited
    assert context.nested_step_module_in_root_visited
    assert context.nested_step_module_in_sub_folder1_visited
    assert context.nested_step_module_in_sub_folder1_sub_folder_visited
    assert context.nested_sub_folder3_visited
    assert context.nested_sub_sub_folder3_visited
