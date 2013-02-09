@echo off
REM ==========================================================================
REM BEHAVE
REM ==========================================================================

setlocal
set HERE=%~dp0
if not defined PYTHON   set PYTHON=python

%PYTHON% %HERE%behave %*
