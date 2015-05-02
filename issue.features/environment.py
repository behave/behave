# -*- coding: UTF-8 -*-
# FILE: features/environment.py
"""
Functionality:

  * active tags
"""

from behave.tag_matcher import ActiveTagMatcher
import six
import sys

# -- MATCHES ANY TAGS: @use.with_{category}={value}
# NOTE: active_tag_value_provider provides category values for active tags.
active_tag_value_provider = {
    "python2": str(six.PY2).lower(),
    "python3": str(six.PY3).lower(),
    "os":      sys.platform,
}
active_tag_matcher = ActiveTagMatcher(active_tag_value_provider)

def setup_active_tag_values(userdata):
    for category in active_tag_value_provider.keys():
        if category in userdata:
            active_tag_value_provider[category] = userdata[category]

def before_all(context):
    # -- SETUP ACTIVE-TAG MATCHER (with userdata): 
    # USE: behave -D browser=safari ...
    # NOT-NEEDED: setup_active_tag_values(context.config.userdata)
    pass

def before_feature(context, feature):
    if active_tag_matcher.should_exclude_with(feature.tags):
        feature.skip(reason=active_tag_matcher.exclude_reason)

def before_scenario(context, scenario):
    if active_tag_matcher.should_exclude_with(scenario.effective_tags):
        scenario.skip(reason=active_tag_matcher.exclude_reason)
