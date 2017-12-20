# -*- coding: UTF-8 -*-
# -- FILE: features/steps/fixture_steps.py

from __future__ import print_function
from behave import when
import os
import sys

# XXX
# # -- VARIANT 1:
# @when(u'I click on ${environment_variable:w}')
# def step_impl(context, environment_variable):
#       env_value = os.environ.get(environment_variable, None)
#       if env_value is None:
#            raise LookupError("Environment variable '%s' is undefined" % environment_variable)
#       print("USE ENVIRONMENT-VAR: %s = %s  (variant 1)" % (environment_variable, env_value))
#
#
# # -- VARIANT 2: Use type converter
# from behave import register_type
# import parse
#
# @parse.with_pattern(r"\$\w+")  # -- ONLY FOR: $WORD
# def parse_environment_var(text):
#     assert text.startswith("$")
#     env_name = text[1:]
#     env_value = os.environ.get(env_name, None)
#     return (env_name, env_value)
#
# register_type(EnvironmentVar=parse_environment_var)
#
# @when(u'I use the environment variable {environment_variable:EnvironmentVar}')
# def step_impl(context, environment_variable):
#       env_name, env_value = environment_variable
#       if env_value is None:
#            raise LookupError("Environment variable '%s' is undefined" % env_name)
#       print("USE ENVIRONMENT-VAR: %s = %s  (variant 2)" \
#             % (env_name, env_value))
#
