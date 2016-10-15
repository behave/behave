tasks/_vendor: Bundled vendor parts -- needed by tasks
===============================================================================

This directory contains bundled archives that may be needed to run the tasks.
Especially, it contains an executable "invoke.zip" archive.
This archive can be used when invoke is not installed.

To execute invoke from the bundled ZIP archive::


    python -m tasks/_vendor/invoke.zip --help
    python -m tasks/_vendor/invoke.zip --version


Example for a local "bin/invoke" script in a UNIX like platform environment::

    #!/bin/bash
    # RUN INVOKE: From bundled ZIP file.

    HERE=$(dirname $0)

    python ${HERE}/../tasks/_vendor/invoke.zip $*

Example for a local "bin/invoke.cmd" script in a Windows environment::

    @echo off
    REM ==========================================================================
    REM RUN INVOKE: From bundled ZIP file.
    REM ==========================================================================

    setlocal
    set HERE=%~dp0
    if not defined PYTHON   set PYTHON=python

    %PYTHON% %HERE%../tasks/_vendor/invoke.zip "%*"
