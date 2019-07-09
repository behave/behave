# -*- coding: UTF-8 -*-

from behave import step

@step(u'{word} step passes')
def step_passes(ctx, word):
    pass

@step(u'{word} step fails')
def step_fails(ctx, word):
    assert False, "XFAIL-STEP: {0} step fails".format(word)
