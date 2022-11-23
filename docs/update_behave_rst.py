#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Generates documentation of behave's

  * command-line options
  * configuration-file parameters

REQUIRES: Python >= 2.6
"""

from __future__ import absolute_import, print_function
import re
import sys
import conf
import textwrap
from behave import configuration
from behave.__main__ import TAG_HELP


positive_number = configuration.positive_number
cmdline = []
config = []
indent = "    "
cmdline_option_schema = """\
.. option:: {cmdline_option}

    {text}
"""
config_param_schema = """\
.. index::
    single: configuration param; {param}

.. describe:: {param} : {type}

    {text}
"""

# -- STEP: Collect information and preprocess it.
for fixed, keywords in configuration.options:
    skip = False
    if "dest" in keywords:
        dest = keywords["dest"]
    else:
        for opt in fixed:
            if opt.startswith("--no"):
                option_case = False
                skip = True
            if opt.startswith("--"):
                dest = opt[2:].replace("-", "_")
                break
            else:
                assert len(opt) == 2
                dest = opt[1:]

    # -- COMMON PART:
    action = keywords.get("action", "store")
    data_type = keywords.get("type", None)
    default_value = keywords.get("default", None)
    if action == "store":
        type = "text"
        if data_type is positive_number:
            type = "positive_number"
        if data_type is int:
            type = "number"
    elif action in ("store_true","store_false"):
        type = "bool"
        default_value = False
        if action == "store_true":
            default_value = True
    elif action == "append":
        type = "sequence<text>"
    else:
        raise ValueError("unknown action %s" % action)

    # -- CASE: command-line option
    text = re.sub(r"\s+", " ", keywords["help"]).strip()
    text = text.replace("%%", "%")
    if default_value and "%(default)s" in text:
        text = text.replace("%(default)s", str(default_value))
    text = textwrap.fill(text, 70, initial_indent="", subsequent_indent=indent)
    if fixed:
        # -- COMMAND-LINE OPTIONS (CONFIGFILE only have empty fixed):
        # cmdline.append(".. option:: %s\n\n%s\n" % (", ".join(fixed), text))
        cmdline_option = ", ".join(fixed)
        cmdline.append(cmdline_option_schema.format(
                            cmdline_option=cmdline_option, text=text))

    if skip or dest in "tags_help lang_list lang_help version".split():
        continue

    # -- CASE: configuration-file parameter
    if action == "store_false":
        # -- AVOID: Duplicated descriptions, use only case:true.
        continue

    text = re.sub(r"\s+", " ", keywords.get("config_help", keywords["help"])).strip()
    text = text.replace("%%", "%")
    if default_value and "%(default)s" in text:
        text = text.replace("%(default)s", str(default_value))
    text = textwrap.fill(text, 70, initial_indent="", subsequent_indent=indent)
    config.append(config_param_schema.format(param=dest, type=type, text=text))


# -- STEP: Generate documentation.
print("Writing behave.rst ...")
with open("behave.rst-template") as f:
    template = f.read()

values = dict(
    cmdline="\n".join(cmdline),
    tag_expression=TAG_HELP,
    config="\n".join(config),
)
with open("behave.rst", "w") as f:
    f.write(template.format(**values))
