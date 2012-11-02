@echo off
REM ==========================================================================
REM 2to3: Convert Python2 to Python3 (part of Python distribution)
REM ==========================================================================

setlocal
set HERE=%~dp0
if not defined PYTHON   set PYTHON=python

%PYTHON% %HERE%2to3.py %*
