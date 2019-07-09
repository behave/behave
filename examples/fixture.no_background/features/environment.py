# -*- coding: UTF-8 -*-
# -- FILE: features/environment.py
import os.path
import sys

# -----------------------------------------------------------------------------
# PYTHON PATH SETUP:
# -----------------------------------------------------------------------------
HERE = os.path.dirname(__file__)
TOPA = os.path.abspath(os.path.join(HERE, ".."))

def setup_python_path():
    sys.path.insert(0, TOPA)

setup_python_path()

# -----------------------------------------------------------------------------
# NORMAL PART:
# -----------------------------------------------------------------------------
from behave_fixture_lib.no_background import behave_no_background
from behave.fixture import use_fixture_by_tag

# -- FIXTURE REGISTRY:
fixture_registry = {
    "fixture.behave.no_background": behave_no_background,
}


# -----------------------------------------------------------------------------
# HOOKS:
# -----------------------------------------------------------------------------
def before_tag(context, tag):
    if tag.startswith("fixture."):
        return use_fixture_by_tag(tag, context, fixture_registry)

