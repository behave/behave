#!/usr/bin/env python

import re
import sys
import conf
import textwrap

sys.argv[0] = 'behave'

from behave import configuration
from behave import __main__

with open('behave.rst-template') as f:
    template = f.read()

#cmdline = configuration.parser.format_help()

config = []
cmdline = []
for fixed, keywords in configuration.options:
    skip = False
    if 'dest' in keywords:
        dest = keywords['dest']
    else:
        for opt in fixed:
            if opt.startswith('--no'):
                skip = True
            if opt.startswith('--'):
                dest = opt[2:].replace('-', '_')
            else:
                assert len(opt) == 2
                dest = opt[1:]

    text = re.sub(r'\s+', ' ', keywords['help']).strip()
    text = text.replace('%%', '%')
    text = textwrap.fill(text, 70, initial_indent='   ', subsequent_indent='   ')
    if fixed:
        # -- COMMAND-LINE OPTIONS (CONFIGFILE only have empty fixed):
        cmdline.append('**%s**\n%s' % (', '.join(fixed), text))

    if skip or dest in 'tags_help lang_list lang_help version'.split():
        continue

    action = keywords.get('action', 'store')
    if action == 'store':
        type = 'text'
    elif action in ('store_true','store_false'):
        type = 'boolean'
    elif action == 'append':
        type = 'text (multiple allowed)'
    else:
        raise ValueError('unknown action %s' % action)

    text = re.sub(r'\s+', ' ', keywords.get('config_help', keywords['help'])).strip()
    text = text.replace('%%', '%')
    text = textwrap.fill(text, 70, initial_indent='   ', subsequent_indent='   ')
    config.append('**%s** -- %s\n%s' % (dest, type, text))


values = dict(
    cmdline='\n'.join(cmdline),
    tag_expression=__main__.TAG_HELP,
    config='\n'.join(config),
)

with open('behave.rst', 'w') as f:
    f.write(template.format(**values))
