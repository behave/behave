# -*- coding: UTF-8 -*-
from __future__ import absolute_import, print_function
from behave import step


@step(u'feature background step_{step_id:d}')
def step_rule_background(ctx, step_id):
    print("feature background step_{0}".format(step_id))


@step(u'rule {rule_id:w} background step_{step_id:d}')
def step_rule_background(ctx, rule_id, step_id):
    print("rule {0} background step_{1}".format(rule_id, step_id))


@step(u'rule {rule_id:w} scenario_{scenario_id:d} step_{step_id:d}')
def step_rule_scenario(ctx, rule_id, scenario_id, step_id):
    print("rule {0} scenario_{1} step_{2}".format(
        rule_id, scenario_id, step_id))


