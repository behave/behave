# -*- coding: UTF-8 -*-

from behave.tag_matcher import ActiveTagMatcher, setup_active_tag_values
from behave.active_tag import python, python_feature


# -- MATCHES ANY TAGS: @use.with_{category}={value}
# NOTE: active_tag_value_provider provides category values for active tags.
active_tag_value_provider = {}
active_tag_value_provider.update(python.ACTIVE_TAG_VALUE_PROVIDER)
active_tag_value_provider.update(python_feature.ACTIVE_TAG_VALUE_PROVIDER)
active_tag_matcher = ActiveTagMatcher(active_tag_value_provider)


# -----------------------------------------------------------------------------
# HOOKS:
# -----------------------------------------------------------------------------
def before_all(context):
    # -- SETUP ACTIVE-TAG MATCHER (with userdata):
    setup_active_tag_values(active_tag_value_provider, context.config.userdata)


def before_feature(context, feature):
    if active_tag_matcher.should_skip(feature):
        feature.skip(reason=active_tag_matcher.skip_reason)

def before_rule(context, rule):
    if active_tag_matcher.should_skip(rule):
        rule.skip(reason=active_tag_matcher.skip_reason)

def before_scenario(context, scenario):
    if active_tag_matcher.should_skip(scenario):
        scenario.skip(reason=active_tag_matcher.skip_reason)

