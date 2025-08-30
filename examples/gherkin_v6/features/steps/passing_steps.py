from behave import step

@step('{word} step passes')
def step_passes(ctx, word):
    pass

@step('{word} step fails')
def step_fails(ctx, word):
    assert False, "XFAIL-STEP: {0} step fails".format(word)
