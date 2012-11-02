@echo off
REM ==========================================================================
REM copytree: Copy a directory tree recursively to a destination dir
REM ==========================================================================

setlocal
set HERE=%~dp0
if not defined PYTHON   set PYTHON=python

%PYTHON% %HERE%copytree.py %*
