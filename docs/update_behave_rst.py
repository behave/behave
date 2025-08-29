#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Generates documentation of behave's

  * command-line options
  * configuration-file parameters

REQUIRES: Python >= 2.7
"""

from __future__ import absolute_import, print_function
import re
import textwrap
from behave import configuration
from behave.__main__ import TAG_EXPRESSIONS_HELP


positive_number = configuration.positive_number
cmdline = []
config = []
indent = "    "
cmdline_option_schema = """\
.. option:: {cmdline_option}

    {text}
"""

config_param_schema_OLD = """\
.. index::
    single: configuration file param; {param}

.. confval:: {param} : {type}

    {text}
"""

# -- NOTE: Using ":type:" parameter for directive is too noisy.
config_param_schema = """\
.. index::
    single: configuration file parameter; {param}

.. confval:: {param} : {type}

    {text}
"""

# -- NOTE: Using ":default:" parameter for directive is too noisy.
config_param_schema_with_default = """\
.. index::
    single: configuration file parameter; {param}

.. confval:: {param}
    :type: {type}
    :default: {default}

    {text}
"""

def is_no_option(fixed_options):
    return any([opt.startswith("--no") for opt in fixed_options])


def make_cmdline_option_line(option_fixed, type_name=None, metavar=None):
    """Build command-line option line for a command-line option."""
    if type_name.startswith("sequence<"):
        # -- APPEND-MODE: Use only item-tpye
        type_name = type_name[len("sequence<"):-1]
    if metavar is None:
        metavar = type_name.upper()

    if type_name == "bool":
        cmdline_option = ", ".join(option_fixed)
    else:

        parts = []
        value_text = metavar
        if value_text:
            value_text = value_text.split()[0]
        for option_item in option_fixed:
            parts.append("{option} {value}".format(option=option_item,
                                                   value=value_text).strip())
        cmdline_option = ", ".join(parts)

    return cmdline_option


# -- STEP: Collect information and preprocess it.
for fixed, keywords in configuration.OPTIONS:
    skip = False
    config_file_param = True
    if is_no_option(fixed):
        # -- EXCLUDE: --no-xxx option
        config_file_param = False

    if "dest" in keywords:
        dest = keywords["dest"]
    else:
        for opt in fixed:
            if opt.startswith("--no"):
                skip = True
            if opt.startswith("--"):
                dest = opt[2:].replace("-", "_")
                break
            else:
                assert len(opt) == 2
                dest = opt[1:]

    # -- COMMON PART:
    type_name_default = "text"
    type_name_map = {
        "color": "Colored (Enum)",
        "tag_expression_protocol": "TagExpressionProtocol (Enum)",
    }
    type_name = "string"
    action = keywords.get("action", "store")
    data_type = keywords.get("type", None)
    default_value = keywords.get("default", None)
    metavar = keywords.get("metavar", None)
    if action in ("store", "store_const"):
        type_name = "text"
        if data_type is positive_number:
            type_name = "positive_number"
        elif data_type is int:
            type_name = "number"
        else:
            type_name = type_name_map.get(dest, type_name_default)
    elif action in ("store_true", "store_false"):
        type_name = "bool"
        default_value = False
        if action == "store_true":
            default_value = True
    elif action == "append":
        type_name = "sequence<text>"
    else:
        raise ValueError("unknown action %s" % action)

    # -- SPECIAL CASE: --no-color
    if action == "store_const":
        metavar = ""    # -- HIDE: metavar info


    # -- CASE: command-line option
    text = re.sub(r"\s+", " ", keywords["help"]).strip()
    text = text.replace("%%", "%")
    if default_value and "%(default)s" in text:
        text = text.replace("%(default)s", str(default_value))
    text = textwrap.fill(text, 70, initial_indent="", subsequent_indent=indent)
    if fixed:
        # -- COMMAND-LINE OPTIONS (CONFIGFILE only have empty fixed):
        # cmdline.append(".. option:: %s\n\n%s\n" % (", ".join(fixed), text))
        cmdline_option = make_cmdline_option_line(fixed,
                                                  type_name=type_name,
                                                  metavar=metavar)
        cmdline.append(cmdline_option_schema.format(
                            cmdline_option=cmdline_option, text=text))

    if skip or dest in configuration.CONFIGFILE_EXCLUDED_OPTIONS:
        continue

    # -- CASE: configuration-file parameter
    if not config_file_param:
        continue

    text = re.sub(r"\s+", " ", keywords.get("config_help", keywords["help"])).strip()
    text = text.replace("%%", "%")
    if default_value and "%(default)s" in text:
        text = text.replace("%(default)s", str(default_value))
    text = textwrap.fill(text, 70, initial_indent="", subsequent_indent=indent)
    this_config_param_schema = config_param_schema
    if default_value:
        # DISABLED: this_config_param_schema = config_param_schema_with_default
        this_config_param_schema = config_param_schema
    config.append(this_config_param_schema.format(param=dest, type=type_name,
                                                  default=default_value,
                                                  text=text))


# -- STEP: Generate documentation.
print("Writing behave.rst ...")
with open("behave.rst-template") as f:
    template = f.read()

values = dict(
    cmdline="\n".join(cmdline),
    tag_expression=TAG_EXPRESSIONS_HELP,
    config="\n".join(config),
)
with open("behave.rst", "w") as f:
    f.write(template.format(**values))
