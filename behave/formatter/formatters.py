# -*- coding: utf-8 -*-

import sys
import codecs
from behave.formatter.base import StreamOpener

# -----------------------------------------------------------------------------
# FORMATTER REGISTRY:
# -----------------------------------------------------------------------------
formatters = {}


def register_as(formatter_class, name):
    """
    Register formatter class with given name.

    :param formatter_class:  Formatter class to register.
    :param name:  Name for this formatter (as identifier).
    """
    formatters[name] = formatter_class

def register(formatter_class):
    register_as(formatter_class, formatter_class.name)


def list_formatters(stream):
    for name in sorted(formatters):
        stream.write(u'%s: %s\n' % (name, formatters[name].description))


def get_formatter(config, stream_openers):
    # -- BUILD: Formatter list
    default_stream_opener = StreamOpener(stream=sys.stdout)
    formatter_list = []
    for i, name in enumerate(config.format):
        stream_opener = default_stream_opener
        if i < len(stream_openers):
            stream_opener = stream_openers[i]
        formatter_list.append(formatters[name](stream_opener, config))
    return formatter_list


# -----------------------------------------------------------------------------
# REGISTER KNOWN FORMATTER:
# -----------------------------------------------------------------------------
from behave.formatter import plain
register(plain.PlainFormatter)
from behave.formatter import pretty
register(pretty.PrettyFormatter)
from behave.formatter import json
register(json.JSONFormatter)
register(json.PrettyJSONFormatter)
from behave.formatter import null
register(null.NullFormatter)

from behave.formatter import progress
register(progress.ScenarioProgressFormatter)
register(progress.StepProgressFormatter)
from behave.formatter.rerun import RerunFormatter
register(RerunFormatter)
from behave.formatter.tag_count import TagCountFormatter, TagLocationFormatter
register(TagCountFormatter)
register(TagLocationFormatter)

from behave.formatter.steps import StepsFormatter
register(StepsFormatter)
