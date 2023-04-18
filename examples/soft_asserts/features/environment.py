# -*- coding: UTF-8 -*-
# FILE: features/environment.py

from __future__ import absolute_import, print_function
import os.path
import sys


HERE = os.path.abspath(os.path.dirname(__file__))
TOP_DIR = os.path.abspath(os.path.join(HERE, "../.."))


# -----------------------------------------------------------------------------
# HOOKS:
# -----------------------------------------------------------------------------
def before_all(context):
    setup_python_path()


def before_scenario(context, scenario):
    if "behave.continue_after_failed_step" in scenario.effective_tags:
        scenario.continue_after_failed_step = True


# -----------------------------------------------------------------------------
# SPECIFIC FUNCTIONALITY:
# -----------------------------------------------------------------------------
def setup_python_path():
    # -- ENSURE: behave4cmd0 can be imported in steps-directory.
    sys.path.insert(0, TOP_DIR)
