# -*- coding: utf-8 -*-
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
    if sys.version_info[0] < 3:
        # py2 does, however, sometimes declare an encoding on sys.stdout,
        # even if it doesn't use it (or it might be explicitly None)
        for i, stream in enumerate(streams):
            encoding = getattr(stream, 'encoding', None) or 'UTF-8'
            streams[i] = codecs.getwriter(encoding)(stream)
    elif not getattr(stream, 'encoding', None):
        # ok, so the stream doesn't have an encoding at all so add one
        for i, stream in enumerate(streams):
            streams[i] = codecs.getwriter('UTF-8')(stream)

    # TODO complete this
    formatter_list = []
    for i in range(len(config.format)):
        name = config.format[i]
        if i < len(streams):
            stream = streams[i]
        else:
            stream = sys.stdout
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
