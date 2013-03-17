# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# HOOKS:
# -----------------------------------------------------------------------------
def before_all(context):
    setup_context_with_global_params_test(context)

# -----------------------------------------------------------------------------
# SPECIFIC FUNCTIONALITY:
# -----------------------------------------------------------------------------
def setup_context_with_global_params_test(context):
    context.global_name = "env:Alice"
    context.global_age  = 12
