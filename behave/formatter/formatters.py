# -*- coding: utf-8 -*-
# pylint: disable=C0111,W0511
#   C0111   missing docstrings
#   W0511   Show TODO statements

import sys
import codecs

# -----------------------------------------------------------------------------
# FORMATTER REGISTRY:
# -----------------------------------------------------------------------------
formatters = {}


def register(formatter):
    formatters[formatter.name] = formatter


def list_formatters(stream):
    for name in sorted(formatters):
        stream.write(u'%s: %s\n' % (name, formatters[name].description))


def get_formatter(config, streams):
    # the stream may already handle encoding (py3k sys.stdout) - if it
    # doesn't (py2k sys.stdout) then make it do so.
    default_encoding = 'UTF-8'
    for i, stream in enumerate(streams):
        if sys.version_info[0] < 3:
            # py2 does, however, sometimes declare an encoding on sys.stdout,
            # even if it doesn't use it (or it might be explicitly None)
            encoding = getattr(stream, 'encoding', None) or default_encoding
            streams[i] = codecs.getwriter(encoding)(stream)
        elif not getattr(stream, 'encoding', None):
            # ok, so the stream doesn't have an encoding at all so add one
            streams[i] = codecs.getwriter(default_encoding)(stream)

    # -- BUILD: Formatter list
    default_stream = sys.stdout
    formatter_list = []
    for i, name in enumerate(config.format):
        stream = default_stream
        if i < len(streams):
            stream = streams[i]
        formatter_list.append(formatters[name](stream, config))
    return formatter_list


# -----------------------------------------------------------------------------
# REGISTER KNOWN FORMATTERS:
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
