#!/usr/bin/env python3
# -- ENSURE: Use local path during development.
import sys
import os.path

# ----------------------------------------------------------------------------
# SETUP PATHS:
# ----------------------------------------------------------------------------
NAME = "behave"
HERE = os.path.dirname(__file__)
TOP  = os.path.join(HERE, "..")
if os.path.isdir(os.path.join(TOP, NAME)):
    sys.path.insert(0, os.path.abspath(TOP))

# ----------------------------------------------------------------------------
# BEHAVE-TWEAKS:
# ----------------------------------------------------------------------------
def setup_behave():
    """
    Apply tweaks, extensions and patches to "behave".
    """
    from behave.configuration import Configuration
    # -- DISABLE: Timings to simplify issue.features/ tests.
    # Configuration.defaults["format0"] = "pretty"
    # Configuration.defaults["format0"] = "progress"
    Configuration.defaults["show_timings"] = False

def behave_main0():
    # from behave.configuration import Configuration
    from behave.__main__ import main as behave_main
    setup_behave()
    return behave_main()

# ----------------------------------------------------------------------------
# MAIN:
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    if "COVERAGE_PROCESS_START" in os.environ:
        import coverage
        coverage.process_startup()
    sys.exit(behave_main0())
