# -*- coding: utf-8 -*-

from __future__ import absolute_import
from behave import then

@then('the behave hook "{hook}" was called')
def step_behave_hook_was_called(context, hook):
    substeps = u'Then the command output should contain "hooks.{0}: "'.format(hook)
    context.execute_steps(substeps)

