# -*- coding: utf-8 -*-
# ============================================================================
# PAVER EXTENSION: Tasks for pychecker, pylint, ...
# ============================================================================
"""
A paver extension that provides pip related tasks:
  - download dependent packages
  - build a local packages index for downloaded packages

EXPECTED OPTIONS STRUCTURE:
   options.pychecker
       .default_args        -- Default args to use (as string).
   options.pylint
       .default_args        -- Default args to use (as string).

REQUIRES:
  * paver  >= 1.0.4
  * pychecker >= 0.8.18
  * pylint >= 0.25

SEE ALSO:
  * http://www.blueskyonmars.com/projects/paver/
  * http://pypi.python.org/pypi/Paver/
  * http://pypi.python.org/pypi/pylint/
  * http://pypi.python.org/pypi/pychecker/
"""

from __future__ import with_statement
from paver.easy import consume_args, error, info, options, path, sh, task
from paver.easy import call_task

# ----------------------------------------------------------------------------
# TASKS:
# ----------------------------------------------------------------------------
@task
@consume_args
def pychecker(args):
    """Run pychecker on sources."""
    if not args:
        args = options.pychecker.default_args.split()

    # -- COLLECT: command options, files
    problematic = []
    cmdopts = []
    files   = []
    for arg in args:
        path_ = path(arg)
        if arg.startswith("-"):
            cmdopts.append(arg)
        elif path_.isdir():
            files.extend(path_.walkfiles("*.py"))
        elif arg.endswith(".py") and path_.exists():
            files.append(arg)
        else:
            error("UNKNOWN FILE: {0}".format(arg))
            problematic.append(arg)

    # -- EXECUTE:
    cmdopts = " ".join(cmdopts)
    for file_ in files:
        try:
            sh("pychecker {opts} {file}".format(opts=cmdopts, file=file_))
        except Exception as e:
            error("FAILURE: {0}".format(e))
            problematic.append(file_)

    # -- SUMMARY:
    if problematic:
        errors = len(problematic)
        error("PYCHECKER FAILED: {0} error(s) occured.".format(errors))
        error("PROBLEMATIC:")
        for file_ in problematic:
            error("  - {0}".format(file_))
    else:
        info("PYCHECKER SUCCESS: {0} file(s).".format(len(files)))

@task
@consume_args
def pylint(args):
    """Run pylint on sources."""
    if not args:
        args = options.pychecker.default_args.split()
    cmdline = " ".join(args)
    sh("pylint %s" % cmdline)

@task
@consume_args
def all_checkers(args):
    """Run all python checkers."""
    call_task("pychecker")
    call_task("pylint")
