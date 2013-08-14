#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utility script to format/beautify one or more JSON files.

REQUIRES: Python >= 2.6 (json module is part of Python standard library)
LICENSE:  BSD
"""

__author__    = "Jens Engel"
__copyright__ = "(c) 2011-2013 by Jens Engel"
VERSION = "0.2.2"

# -- IMPORTS:
import os.path
import glob
import logging
from   optparse import OptionParser
import sys
try:
    import json
except ImportError:
    import simplejson as json   #< BACKWARD-COMPATIBLE: Python <= 2.5


# ----------------------------------------------------------------------------
# CONSTANTS:
# ----------------------------------------------------------------------------
DEFAULT_INDENT_SIZE = 2

# ----------------------------------------------------------------------------
# FUNCTIONS:
# ----------------------------------------------------------------------------
def json_format(filename, indent=DEFAULT_INDENT_SIZE, **kwargs):
    """
    Format/Beautify a JSON file.

    :param filename:    Filename of a JSON file to process.
    :param indent:      Number of chars to indent per level (default: 4).
    :returns: >= 0, if successful (written=1, skipped=2). Zero(0), otherwise.
    :raises:  ValueError,           if parsing JSON file contents fails.
    :raises:  json.JSONDecodeError, if parsing JSON file contents fails.
    :raises:  IOError (Error 2), if file not found.
    """
    console  = kwargs.get("console", logging.getLogger("console"))
    encoding = kwargs.get("encoding", None)
    dry_run  = kwargs.get("dry_run", False)
    if indent is None:
        sort_keys = False
    else:
        sort_keys = True

    message = "%s ..." % filename
#    if not (os.path.exists(filename) and os.path.isfile(filename)):
#        console.error("%s ERROR: file not found.", message)
#        return 0

    contents = open(filename, "r").read()
    data      = json.loads(contents, encoding=encoding)
    contents2 = json.dumps(data, indent=indent, sort_keys=sort_keys)
    contents2 = contents2.strip()
    contents2 = "%s\n" % contents2
    if contents == contents2:
        console.info("%s SKIP (already pretty)", message)
        return 2 #< SKIPPED.
    elif not dry_run:
        outfile = open(filename, "w")
        outfile.write(contents2)
        outfile.close()
        console.warn("%s OK", message)
        return 1 #< OK

def json_formatall(filenames, indent=DEFAULT_INDENT_SIZE, dry_run=False):
    """
    Format/Beautify a JSON file.

    :param filenames:  Format one or more JSON files.
    :param indent:     Number of chars to indent per level (default: 4).
    :returns:  0, if successful. Otherwise, number of errors.
    """
    errors = 0
    console = logging.getLogger("console")
    for filename in filenames:
        try:
            result = json_format(filename, indent=indent, console=console,
                                 dry_run=dry_run)
            if not result:
                errors += 1
#        except json.decoder.JSONDecodeError, e:
#            console.error("ERROR: %s (filename: %s)", e, filename)
#            errors += 1
        except StandardError, e:
            console.error("ERROR %s: %s (filename: %s)",
                          e.__class__.__name__, e, filename)
            errors += 1
    return errors

# ----------------------------------------------------------------------------
# MAIN FUNCTION:
# ----------------------------------------------------------------------------
def main(args=None):
    """Boilerplate for this script."""
    if args is None:
        args = sys.argv[1:]

    usage_ = """%prog [OPTIONS] JsonFile [MoreJsonFiles...]
Format/Beautify one or more JSON file(s)."""
    parser = OptionParser(usage=usage_, version=VERSION)
    parser.add_option("-i", "--indent", dest="indent_size",
                default=DEFAULT_INDENT_SIZE, type="int",
                help="Indent size to use (default: %default).")
    parser.add_option("-c", "--compact", dest="compact",
                action="store_true", default=False,
                help="Use compact format (default: %default).")
    parser.add_option("-n", "--dry-run", dest="dry_run",
                action="store_true", default=False,
                help="Check only if JSON is well-formed (default: %default).")
    options, filenames = parser.parse_args(args)    #< pylint: disable=W0612
    if not filenames:
        parser.error("OOPS, no filenames provided.")
    if options.compact:
        options.indent_size = None

    # -- STEP: Init logging subsystem.
    format_ = "json.format: %(message)s"
    logging.basicConfig(level=logging.WARN, format=format_)
    console = logging.getLogger("console")

    # -- DOS-SHELL SUPPORT: Perform filename globbing w/ wildcards.
    skipped = 0
    filenames2 = []
    for filename in filenames:
        if "*" in filenames:
            files = glob.glob(filename)
            filenames2.extend(files)
        elif os.path.isdir(filename):
            # -- CONVENIENCE-SHORTCUT: Use DIR as shortcut for JSON files.
            files = glob.glob(os.path.join(filename, "*.json"))
            filenames2.extend(files)
            if not files:
                console.info("SKIP %s, no JSON files found in dir.", filename)
                skipped += 1
        elif not os.path.exists(filename):
            console.warn("SKIP %s, file not found.", filename)
            skipped += 1
            continue
        else:
            assert os.path.exists(filename)
            filenames2.append(filename)
    filenames = filenames2

    # -- NORMAL PROCESSING:
    errors  = json_formatall(filenames, options.indent_size,
                             dry_run=options.dry_run)
    console.error("Processed %d files (%d with errors, skipped=%d).",
                  len(filenames), errors, skipped)
    if not filenames:
        errors += 1
    return errors

# ----------------------------------------------------------------------------
# AUTO-MAIN:
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())
