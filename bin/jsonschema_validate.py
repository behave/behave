#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Validate a JSON file against its JSON schema.

SEE ALSO:
  * https://python-jsonschema.readthedocs.org/
  * https://python-jsonschema.readthedocs.org/en/latest/errors.html

REQUIRES:
  Python >= 2.6
  jsonschema >= 1.3.0
  argparse
"""

from __future__ import absolute_import, print_function

__author__  = "Jens Engel"
__version__ = "0.1.0"

from jsonschema import validate
import argparse
import os.path
import sys
import textwrap
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        sys.exit("REQUIRE: simplejson (which is not installed)")


# -----------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------
HERE = os.path.dirname(__file__)
TOP  = os.path.normpath(os.path.join(HERE, ".."))
SCHEMA = os.path.join(TOP, "etc", "json", "behave.json-schema")


# -----------------------------------------------------------------------------
# FUNCTIONS:
# -----------------------------------------------------------------------------
def jsonschema_validate(filename, schema, encoding=None):
    f = open(filename, "r")
    contents = f.read()
    f.close()
    data = json.loads(contents, encoding=encoding)
    return validate(data, schema)


def main(args=None):
    """
    Validate JSON files against their JSON schema.
    NOTE: Behave's JSON-schema is used per default.

    SEE ALSO:
      * http://json-schema.org/
      * http://tools.ietf.org/html/draft-zyp-json-schema-04
    """
    if args is None:
        args = sys.argv[1:]
    default_schema = None
    if os.path.exists(SCHEMA):
        default_schema = SCHEMA

    parser = argparse.ArgumentParser(
                description=textwrap.dedent(main.__doc__),
                formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-v", "--version",
                        action="version", version=__version__)
    parser.add_argument("-s", "--schema",
                        help="JSON schema to use.")
    parser.add_argument("-e", "--encoding",
                        help="Encoding for JSON/JSON schema.")
    parser.add_argument("files", nargs="+", metavar="JSON_FILE",
                        help="JSON file to check.")
    parser.set_defaults(
            schema=default_schema,
            encoding="UTF-8"
    )
    options = parser.parse_args(args)
    if not options.schema:
        parser.error("REQUIRE: JSON schema")
    elif not os.path.isfile(options.schema):
        parser.error("SCHEMA not found: %s" % options.schema)

    try:
        f = open(options.schema, "r")
        contents = f.read()
        f.close()
        schema = json.loads(contents, encoding=options.encoding)
    except Exception as e:
        msg = "ERROR: %s: %s (while loading schema)" % (e.__class__.__name__, e)
        sys.exit(msg)

    error_count = 0
    for filename in options.files:
        validated = True
        more_info = None
        try:
            print("validate:", filename, "...", end=' ')
            jsonschema_validate(filename, schema, encoding=options.encoding)
        except Exception as e:
            more_info = "%s: %s" % (e.__class__.__name__, e)
            validated = False
            error_count += 1
        if validated:
            print("OK")
        else:
            print("FAILED\n\n%s" % more_info)
    return error_count


# -----------------------------------------------------------------------------
# AUTO-MAIN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())
