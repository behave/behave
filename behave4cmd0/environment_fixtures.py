# -*- coding: UTF-8
"""
Provides behave fixtures related to environment and environment variables.
"""

from __future__ import absolute_import, print_function
import os
from behave.fixture import fixture


# -----------------------------------------------------------------------------
# FIXTURE SUPPORT
# -----------------------------------------------------------------------------
SCOPE_NAMES = ("scenario", "rule", "feature")

def get_scope_name_from_context(ctx):
    for scope_name in SCOPE_NAMES:
        scope_value = getattr(ctx, scope_name, None)
        if scope_value is not None:
            return scope_name
    # -- NOT FOUND:
    return "testrun"


class ScopedEnvironment(object):
    """Store current environment variables and restore them afterwards."""
    def __init__(self, env=None):
        if env is None:
            env = os.environ.copy()
        self.initial_env = env
        self.restored = False

    def restore_environment(self):
        if not self.restored:
            os.environ.clear()
            os.environ.update(self.initial_env)
        self.restored = True


# -----------------------------------------------------------------------------
# FIXTURES
# -----------------------------------------------------------------------------
@fixture
def scoped_environment(ctx, scope_name=None):
    """
    Provide fixture for a scenario/rule/fixture that:

    * Stores the current environment variables and
    * Restore them after the scenario is finished
    """
    if scope_name is None:
        # -- AUTO-DETECT: Current scope -- scenario, rule or feature
        scope_name = get_scope_name_from_context(ctx)

    scoped_env_name = "{}_scoped_environment".format(scope_name)
    scoped_env_counter_name = "{}_count".format(scoped_env_name)
    count = ctx.use_or_assign_param(scoped_env_counter_name, 0)
    if not count:
        # -- ONLY-ONCE: Perform only first store and restore cleanup of environment.
        scoped_env = ScopedEnvironment()
        ctx.add_cleanup(scoped_env.restore_environment)
        setattr(ctx, scoped_env_name, scoped_env)
        setattr(ctx, scoped_env_counter_name, 1)
        return scoped_env
    # -- OTHERWISE: scoped_environment is already set-up.
    scoped_env = getattr(ctx, scoped_env_name, None)
    return scoped_env

# -----------------------------------------------------------------------------
# FIXTURE-TAG REGISTRY: Register fixture by fixture-tag name
# -----------------------------------------------------------------------------
# -- REGISTRY DATA SCHEMA 1: fixture_func
fixture_registry1 = {
    "fixture.scoped_environment": scoped_environment,
}
