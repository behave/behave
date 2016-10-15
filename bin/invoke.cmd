@echo off
REM RUN INVOKE: From bundled ZIP file.

setlocal
set HERE=%~dp0
set INVOKE_TASKS_USE_VENDOR_BUNDLES="yes"
if not defined PYTHON   set PYTHON=python

%PYTHON% %HERE%../tasks/_vendor/invoke.zip "%*"
