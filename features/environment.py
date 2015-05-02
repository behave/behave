# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# HOOKS:
# -----------------------------------------------------------------------------
def before_all(context):
    setup_python_path()
    setup_context_with_global_params_test(context)

# -----------------------------------------------------------------------------
# SPECIFIC FUNCTIONALITY:
# -----------------------------------------------------------------------------
def setup_context_with_global_params_test(context):
    context.global_name = "env:Alice"
    context.global_age  = 12

def setup_python_path():
    # -- NEEDED-FOR: formatter.user_defined.feature
    import os
    PYTHONPATH = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = "."+ os.pathsep + PYTHONPATH
