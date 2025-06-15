from __future__ import absolute_import, print_function
import os
from behave._types import parse_bool


__status__ = "WIP"

# -----------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------
STORE_CAPTURED_ALWAYS = parse_bool(
    os.environ.get("BEHAVE_STORE_CAPTURED_ALWAYS", "ON")
)
SHOW_CAPTURED_ALWAYS = parse_bool(
    os.environ.get("BEHAVE_SHOW_CAPTURED_ALWAYS", "OFF")
)
ANY_HOOK_STORE_CAPTURED_ON_SUCCESS = parse_bool(
    os.environ.get("BEHAVE_HOOK_STORE_CAPTURED_ON_SUCCESS", "OFF")
)
ANY_HOOK_SHOW_CAPTURED_ON_SUCCESS = parse_bool(
    os.environ.get("BEHAVE_HOOK_SHOW_CAPTURED_ON_SUCCESS", "OFF")
)

# -- IDEA:
ANY_HOOK_STORE_CLEANUP_ON_SUCCESS = parse_bool(
    os.environ.get("BEHAVE_HOOK_STORE_CLEANUP_ON_SUCCESS", "OFF")
)

# -- DERIVED:
CAPTURE_SINK_STORE_CAPTURED_ON_SUCCESS = STORE_CAPTURED_ALWAYS
CAPTURE_SINK_SHOW_CAPTURED_ON_SUCCESS = SHOW_CAPTURED_ALWAYS
