# -- NEEDED-BY: features/i18n_emoji.feature
from behave import given


@given('🎸')
def step_impl(context):
    """Step implementation example with emoji(s)."""
    pass

