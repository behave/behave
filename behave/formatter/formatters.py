import sys
import codecs

formatters = {}


def register(formatter):
    formatters[formatter.name] = formatter


def list_formatters(stream):
    for name in formatters:
        stream.write(u'%s: %s\n' % (name, formatters[name].description))


def get_formatter(config, stream):
    # the stream may already handle encoding (py3k sys.stdout) - if it
    # doesn't (py2k sys.stdout) then make it do so.
    if sys.version_info[0] < 3:
        # py2 does, however, sometimes declare an encoding on sys.stdout,
        # even if it doesn't use it (or it might be explicitly None)
        encoding = getattr(stream, 'encoding', None) or 'UTF-8'
        stream = codecs.getwriter(encoding)(stream)
    elif not getattr(stream, 'encoding', None):
        # ok, so the stream doesn't have an encoding at all so add one
        stream = codecs.getwriter('UTF-8')(stream)

    # TODO complete this
    formatter = None
    for name in config.format:
        if formatter is None:
            formatter = formatters[name](stream, config)
        else:
            formatter = formatters[name](formatter, config)
    return formatter

from behave.formatter import plain
register(plain.PlainFormatter)
from behave.formatter import pretty
register(pretty.PrettyFormatter)
from behave.formatter import json
register(json.JSONFormatter)
