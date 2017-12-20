# -*- coding: UTF-8 -*-
"""
Provides "invoke" script when invoke is not installed.
Note that this approach uses the "tasks/_vendor/invoke.zip" bundle package.

Usage::

    # -- INSTEAD OF: invoke command
    # Show invoke version
    python -m tasks --version

    # List all tasks
    python -m tasks -l

.. seealso::

    * http://pyinvoke.org
    * https://github.com/pyinvoke/invoke


Examples for Invoke Scripts using the Bundle
-------------------------------------------------------------------------------

For UNIX like platforms:

.. code-block:: sh

    #!/bin/sh
    #!/bin/bash
    # RUN INVOKE: From bundled ZIP file (with Bourne shell/bash script).
    # FILE: invoke.sh (in directory that contains tasks/ directory)

    HERE=$(dirname $0)
    export INVOKE_TASKS_USE_VENDOR_BUNDLES="yes"

    python ${HERE}/tasks/_vendor/invoke.zip $*


For Windows platform:

.. code-block:: bat

    @echo off
    REM RUN INVOKE: From bundled ZIP file (with Windows Batchfile).
    REM FILE: invoke.cmd (in directory that contains tasks/ directory)

    setlocal
    set HERE=%~dp0
    set INVOKE_TASKS_USE_VENDOR_BUNDLES="yes"
    if not defined PYTHON   set PYTHON=python

    %PYTHON% %HERE%tasks/_vendor/invoke.zip "%*"
"""

from __future__ import absolute_import
import os
import sys

# -----------------------------------------------------------------------------
# BOOTSTRAP PATH: Use provided vendor bundle if "invoke" is not installed
# -----------------------------------------------------------------------------
# NOTE: tasks/__init__.py performs sys.path setup.
os.environ["INVOKE_TASKS_USE_VENDOR_BUNDLES"] = "yes"

# -----------------------------------------------------------------------------
# AUTO-MAIN:
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    from invoke.main import program
    sys.exit(program.run())
