"""
Test support functionality with good or bad hook and fixtures implementations.
Currently used by capture related tests.
"""

from behave import fixture, use_fixture
from tests.functional.error import SomeError


# ----------------------------------------------------------------------------
# TEST SUPPORT: FEATURE HOOKS
# ----------------------------------------------------------------------------
def good_before_feature(ctx, feature):
    print("CALLED-HOOK: {} -- before_feature".format(feature.name))


def good_after_feature(ctx, feature):
    print("CALLED-HOOK: {} -- after_feature".format(feature.name))


# ----------------------------------------------------------------------------
# TEST SUPPORT: RULE HOOKS
# ----------------------------------------------------------------------------
def good_before_rule(ctx, rule):
    print("CALLED-HOOK: {} -- before_rule".format(rule.name))


def good_after_rule(ctx, rule):
    print("CALLED-HOOK: {} -- after_rule".format(rule.name))


# ----------------------------------------------------------------------------
# TEST SUPPORT: SCENARIO HOOKS
# ----------------------------------------------------------------------------
def good_before_scenario(ctx, scenario):
    print("CALLED-HOOK: {} -- before_scenario".format(scenario.name))


def good_after_scenario(ctx, scenario):
    print("CALLED-HOOK: {} -- after_scenario".format(scenario.name))


def bad_after_scenario_error(ctx, scenario):
    print("BAD-HOOK: {} -- after_scenario".format(scenario.name))
    raise SomeError("OOPS, ERROR in {}".format(scenario.name))


def bad_before_scenario_failed(ctx, scenario):
    print("BAD-HOOK: {} -- before_scenario".format(scenario.name))
    assert False, "OOPS, FAILED in {}".format(scenario.name)


# ----------------------------------------------------------------------------
# TEST SUPPORT: FIXTURES used by HOOKS (using fixture-tags)
# ----------------------------------------------------------------------------
@fixture
def good_fixture(ctx, name):
    print("FIXTURE-SETUP: {}".format(name))
    yield
    print("FIXTURE-CLEANUP: {}".format(name))


@fixture
def bad_fixture_setup(ctx, name):
    try:
        print("BAD_FIXTURE-SETUP: {}".format(name))
        raise SomeError("OOPS, ERROR in {}".format(name))
        yield
    finally:
        # -- ENSURE: Cleanup part is called.
        print("FIXTURE-CLEANUP: {}".format(name))


@fixture
def bad_fixture_cleanup(ctx, name):
    print("FIXTURE-SETUP: {}".format(name))
    yield
    print("BAD_FIXTURE-CLEANUP: {}".format(name))
    raise SomeError("OOPS, ERROR in {}".format(name))


# ----------------------------------------------------------------------------
# TEST SUPPORT: HOOKS -- TAGS
# ----------------------------------------------------------------------------
def before_any_tag(ctx, tag):
    if tag.startswith("good_fixture"):
        use_fixture(good_fixture, ctx, tag)
    elif tag.startswith("bad_fixture_setup"):
        use_fixture(bad_fixture_setup, ctx, tag)
    elif tag.startswith("bad_fixture_cleanup"):
        use_fixture(bad_fixture_cleanup, ctx, tag)
    else:
        print("CALLED-HOOK: tag={}".format(tag))


def after_any_tag(ctx, tag):
    if tag.startswith("bad_after_tag"):
        print("BAD-HOOK: tag={}".format(tag))
        raise SomeError("OOPS, ERROR in {}".format(tag))
