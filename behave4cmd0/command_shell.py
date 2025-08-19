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

from behave4cmd0.__setup import TOP
import os.path
import subprocess
import sys
import shlex


# -----------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------
# OR: BEHAVE_CMD_DEFAULT = "-mbehave"
BEHAVE_CMD_DEFAULT = "-mbehave"
BEHAVE_SEARCH_PATH = [os.getcwd(), TOP]


def get_behave_cmd(search_path=None):
    if search_path is None:
        search_path = BEHAVE_SEARCH_PATH

    behave_cmd = BEHAVE_CMD_DEFAULT
    for directory in search_path:
        this_behave_cmd = os.path.normpath("{0}/bin/behave".format(directory))
        if os.path.exists(this_behave_cmd):
            behave_cmd = this_behave_cmd
            break
    # -- DIAG: print("USING behave_cmd: {}".format(behave_cmd))
    return behave_cmd


# -----------------------------------------------------------------------------
# CLASSES:
# -----------------------------------------------------------------------------
class CommandResult(object):
    """
    ValueObject to store the results of a subprocess command call.
    """
    def __init__(self, **kwargs):
        self.command = kwargs.pop("command", None)
        self.returncode = kwargs.pop("returncode", 0)
        self.stdout = kwargs.pop("stdout", "")
        self.stderr = kwargs.pop("stderr", "")
        self._output = None
        if kwargs:
            names = ", ".join(kwargs.keys())
            raise ValueError("Unexpected: %s" % names)

    @property
    def output(self):
        if self._output is None:
            output = self.stdout
            if self.stderr:
                if self.stdout:
                    output += "\n"
                output += self.stderr
            self._output = output
        return self._output

    @property
    def failed(self):
        return self.returncode != 0

    def clear(self):
        self.command = None
        self.returncode = 0
        self.stdout = ""
        self.stderr = ""
        self._output = None


class Command(object):
    """
    Helper class to run commands as subprocess,
    collect their output and subprocess returncode.
    """
    DEBUG = False
    COMMAND_MAP = {
        "behave": "{python} {behave_cmd}".format(
            python=sys.executable, behave_cmd=get_behave_cmd()
        ),
    }
    PREPROCESSOR_MAP = {}
    POSTPROCESSOR_MAP = {}
    USE_SHELL = sys.platform.startswith("win")

    @staticmethod
    def preprocess_command(preprocessors, cmdargs, command=None, cwd="."):
        if not os.path.isdir(cwd):
            return cmdargs
        elif not command:
            command = " ".join(cmdargs)

        for preprocess in preprocessors:
            cmdargs = preprocess(command, cmdargs, cwd)
        return cmdargs

    @staticmethod
    def postprocess_command(postprocessors, command_result):
        for postprocess in postprocessors:
            command_result = postprocess(command_result)
        return command_result

    @classmethod
    def run(cls, command, cwd=".", **kwargs):
        """
        Make a subprocess call, collect its output and returncode.
        Returns CommandResult instance as ValueObject.
        """
        assert isinstance(command, str)
        command_result = CommandResult()
        command_result.command = command
        use_shell = cls.USE_SHELL
        if "shell" in kwargs:
            use_shell = kwargs.pop("shell")

        # -- BUILD COMMAND ARGS:
        cmdargs = shlex.split(command)

        # -- TRANSFORM COMMAND (optional)
        command0 = cmdargs[0]
        real_command = cls.COMMAND_MAP.get(command0, None)
        if real_command:
            cmdargs0 = real_command.split()
            cmdargs = cmdargs0 + cmdargs[1:]
        preprocessors = cls.PREPROCESSOR_MAP.get(command0)
        if preprocessors:
            cmdargs = cls.preprocess_command(preprocessors, cmdargs, command, cwd)


        # -- RUN COMMAND:
        try:
            process = subprocess.Popen(cmdargs,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True,
                            shell=use_shell,
                            cwd=cwd, **kwargs)
            out, err = process.communicate()
            process.poll()
            assert process.returncode is not None
            command_result.stdout = out
            command_result.stderr = err
            command_result.returncode = process.returncode
            if cls.DEBUG:
                print("shell.cwd={0}".format(kwargs.get("cwd", None)))
                print("shell.command: {0}".format(" ".join(cmdargs)))
                print("shell.command.output:\n{0};".format(command_result.output))
        except OSError as e:
            command_result.stderr = "OSError: %s" % e
            command_result.returncode = e.errno
            assert e.errno != 0

        postprocessors = cls.POSTPROCESSOR_MAP.get(command0)
        if postprocessors:
            command_result = cls.postprocess_command(postprocessors, command_result)
        return command_result


# -----------------------------------------------------------------------------
# PREPROCESSOR:
# -----------------------------------------------------------------------------
def path_glob(command, cmdargs, cwd="."):
    import glob
    if not glob.has_magic(command):
        return cmdargs

    assert os.path.isdir(cwd)
    try:
        current_cwd = os.getcwd()
        os.chdir(cwd)
        new_cmdargs = []
        for cmdarg in cmdargs:
            if not glob.has_magic(cmdarg):
                new_cmdargs.append(cmdarg)
                continue

            more_args = glob.glob(cmdarg)
            if more_args:
                new_cmdargs.extend(more_args)
            else:
                # -- BAD-CASE: Require at least one match.
                # Otherwise, restore original arg.
                new_cmdargs.append(cmdarg)

        cmdargs = new_cmdargs
    finally:
        os.chdir(current_cwd)
    return cmdargs

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
    assert isinstance(cmdline, str)
    return run("behave " + cmdline, cwd=cwd, **kwargs)

# -----------------------------------------------------------------------------
# TEST MAIN:
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    command = " ".join(sys.argv[1:])
    output = Command.run(sys.argv[1:])
    print("command: {0}\n{1}\n".format(command, output))
