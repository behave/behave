from behave import step

# -- STEP DEFINITIONS: Use ALTERNATIVES
@step("I am on the profile customisation/settings page")
def step_on_profile_settings_page(ctx):
    print("STEP: Given I am on profile ... page")
