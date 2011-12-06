#!/usr/bin/env python

import re
import conf
import textwrap

from behave import configuration

with open('behave.rst-template') as f:
    template = f.read()

cmdline = configuration.parser.format_help()

config = []
for fixed, keywords in configuration.options:
    if 'dest' in keywords:
        dest = keywords['dest']
    else:
        for opt in fixed:
            if opt.startswith('--'):
                dest = opt[2:].replace('-', '_')
            else:
                assert len(opt) == 2
                dest = opt[1:]

    if dest in 'tags_help lang_list lang_help version'.split():
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

    text = re.sub(r'\s+', ' ', keywords['help']).strip()
    text = text.replace('%%', '%')
    text = textwrap.fill(text, 70, initial_indent='   ', subsequent_indent='   ')
    config.append('**%s** -- %s\n%s' % (dest, type, text))


values = dict(
    cmdline=cmdline,
    config='\n'.join(config),
)

with open('behave.rst', 'w') as f:
    f.write(template.format(**values))
