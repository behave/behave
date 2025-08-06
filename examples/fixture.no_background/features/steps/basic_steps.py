from behave import given, step

# @step('{word} step passes')
# def step_passes_with_word(context, word):
#     pass

@step('{word} background step passes')
def step_background_step_passes(context, word):
    pass

@given('I need {word} scenario setup')
def step_given_i_need_scenario_setup(context, word):
    pass
