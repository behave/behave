#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Provide a behave shell to simplify creation of feature files
and running features, etc.

    context.command_result = behave_shell.behave(cmdline, cwd=context.workdir)
    behave_shell.create_scenario(scenario_text, cwd=context.workdir)
    behave_shell.create_step_definition(context.text, cwd=context.workdir)
    context.command_result = behave_shell.run_feature_with_formatter(
            context.features[0], formatter=formatter, cwd=context.workdir)

"""

from __future__ import print_function, with_statement
import os.path
import subprocess
import sys
import shlex
import codecs

HERE = os.path.dirname(__file__)
TOP  = os.path.join(HERE, "..", "..")

# -----------------------------------------------------------------------------
# CLASSES:
# -----------------------------------------------------------------------------
class CommandResult(object):
    """
    ValueObject to store the results of a subprocess command call.
    """
    def __init__(self, **kwargs):
        self.command = kwargs.get("command", None)
        self.returncode = kwargs.get("returncode", 0)
        self.output = kwargs.get("output", "")
        self.failed = kwargs.get("failed", bool(self.returncode != 0))

    def clear(self):
        self.command = None
        self.returncode = 0
        self.output = ""
        self.failed = False

class Command(object):
    """
    Helper class to run commands as subprocess,
    collect their output and subprocess returncode.
    """
    DEBUG = False
    COMMAND_MAP = {
        "behave": os.path.normpath("{0}/bin/behave".format(TOP))
    }

    @staticmethod
    def subprocess_check_output(args, **kwargs):
        """
        Reimplement subprocess.check_output() for Python versions
        that do not support it yet (Python2.6, ...).
        """
        # print("RUN: {0}".format(" ".join(args)))
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.STDOUT
        command_process = subprocess.Popen(args, **kwargs)
        output = command_process.communicate()[0]
        command_process.poll()
        assert command_process.returncode is not None
        print("result={0}, OUTPUT:\n{1}\n".format(command_process.returncode, output))
        if command_process.returncode == 0:
            # -- SUCCESSFUL EXECUTION:
            return output
        # -- COMMAND-FAILED: Raise exception
        cmd = " ".join(args)
        e = subprocess.CalledProcessError(command_process.returncode, cmd)
        e.output = output
        raise e


    @classmethod
    def run(cls, command, cwd=".", **kwargs):
        """
        Make a subprocess call, collect its output and returncode.
        Returns CommandResult instance as ValueObject.
        """
        assert isinstance(command, basestring)
        command_result = CommandResult()
        command_result.command = command

        # -- BUILD COMMAND ARGS:
        if isinstance(command, unicode):
            command = codecs.encode(command)
        cmdargs = shlex.split(command)

        # -- TRANSFORM COMMAND (optional)
        real_command = cls.COMMAND_MAP.get(cmdargs[0], None)
        if real_command:
            cmdargs[0] = real_command

        # -- RUN COMMAND:
        try:
            subprocess_check_output = getattr(subprocess, "check_output",
                                            cls.subprocess_check_output)
            stderr = kwargs.pop("stderr", subprocess.STDOUT)
            command_result.output = subprocess_check_output(cmdargs,
                stderr=stderr, cwd=cwd, **kwargs)
            command_result.returncode = 0
            command_result.failed = False
            if cls.DEBUG:
                print("shell.cwd={0}".format(kwargs.get("cwd", None)))
                print("shell.command: {0}".format(" ".join(cmdargs)))
                print("shell.command.output:\n{0};".format(command_result.output))
        except subprocess.CalledProcessError, e:
            command_result.output = e.output
            command_result.returncode = e.returncode
            command_result.failed = True
        except OSError, e:
            command_result.returncode = e.errno
            command_result.failed = True
        return command_result


# -----------------------------------------------------------------------------
# FUNCTIONS:
# -----------------------------------------------------------------------------
def run(command, cwd=".", **kwargs):
    return Command.run(command, cwd=cwd, **kwargs)

def behave(cmdline, cwd=".", **kwargs):
    """
    Run behave as subprocess command and return process/shell instance
    with results (collected output, returncode).
    """
    assert isinstance(cmdline, basestring)
    return run("behave " + cmdline, cwd=cwd, **kwargs)

# -----------------------------------------------------------------------------
# TEST MAIN:
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    command = " ".join(sys.argv[1:])
    output = Command.subprocess_check_output(sys.argv[1:])
    print("command: {0}\n{1}\n".format(command, output))
