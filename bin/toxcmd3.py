#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Provides a command container for additional tox commands, used in "tox.ini".

COMMANDS:

  * copytree
  * copy
  * py2to3

REQUIRES:
  * argparse
"""

from glob import glob
import argparse
import inspect
import os.path
import shutil
import sys
import collections

__author__ = "Jens Engel"
__copyright__ = "(c) 2013 by Jens Engel"
__license__ = "BSD"

# -----------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------
VERSION = "0.1.0"
FORMATTER_CLASS = argparse.RawDescriptionHelpFormatter


# -----------------------------------------------------------------------------
# SUBCOMMAND: copytree
# -----------------------------------------------------------------------------
def command_copytree(args):
    """
    Copy one or more source directory(s) below a destination directory.
    Parts of the destination directory path are created if needed.
    Similar to the UNIX command: 'cp -R srcdir destdir'
    """
    for srcdir in args.srcdirs:
        basename = os.path.basename(srcdir)
        destdir2 = os.path.normpath(os.path.join(args.destdir, basename))
        if os.path.exists(destdir2):
            shutil.rmtree(destdir2)
        sys.stdout.write("copytree: %s => %s\n" % (srcdir, destdir2))
        shutil.copytree(srcdir, destdir2)
    return 0


def setup_parser_copytree(parser):
    parser.add_argument("srcdirs", nargs="+", help="Source directory(s)")
    parser.add_argument("destdir", help="Destination directory")


command_copytree.usage = "%(prog)s srcdir... destdir"
command_copytree.short = "Copy source dir(s) below a destination directory."
command_copytree.setup_parser = setup_parser_copytree


# -----------------------------------------------------------------------------
# SUBCOMMAND: copy
# -----------------------------------------------------------------------------
def command_copy(args):
    """
    Copy one or more source-files(s) to a destpath (destfile or destdir).
    Destdir mode is used if:
      * More than one srcfile is provided
      * Last parameter ends with a slash ("/").
      * Last parameter is an existing directory

    Destination directory path is created if needed.
    Similar to the UNIX command: 'cp srcfile... destpath'
    """
    sources = args.sources
    destpath = args.destpath
    source_files = []
    for file_ in sources:
        if "*" in file_:
            selected = glob(file_)
            source_files.extend(selected)
        elif os.path.isfile(file_):
            source_files.append(file_)

    if destpath.endswith("/") or os.path.isdir(destpath) or len(sources) > 1:
        # -- DESTDIR-MODE: Last argument is a directory.
        destdir = destpath
    else:
        # -- DESTFILE-MODE: Copy (and rename) one file.
        assert len(source_files) == 1
        destdir = os.path.dirname(destpath)

    # -- WORK-HORSE: Copy one or more files to destpath.
    if not os.path.isdir(destdir):
        sys.stdout.write("copy: Create dir %s\n" % destdir)
        os.makedirs(destdir)
    for source in source_files:
        destname = os.path.join(destdir, os.path.basename(source))
        sys.stdout.write("copy: %s => %s\n" % (source, destname))
        shutil.copy(source, destname)
    return 0


def setup_parser_copy(parser):
    parser.add_argument("sources", nargs="+", help="Source files.")
    parser.add_argument("destpath", help="Destination path")


command_copy.usage = "%(prog)s sources... destpath"
command_copy.short = "Copy one or more source files to a destinition."
command_copy.setup_parser = setup_parser_copy


# -----------------------------------------------------------------------------
# SUBCOMMAND: mkdir
# -----------------------------------------------------------------------------
def command_mkdir(args):
    """
    Create a non-existing directory (or more ...).
    If the directory exists, the step is skipped.
    Similar to the UNIX command: 'mkdir -p dir'
    """
    errors = 0
    for directory in args.dirs:
        if os.path.exists(directory):
            if not os.path.isdir(directory):
                # -- SANITY CHECK: directory exists, but as file...
                sys.stdout.write("mkdir: %s\n" % directory)
                sys.stdout.write("ERROR: Exists already, but as file...\n")
                errors += 1
        else:
            # -- NORMAL CASE: Directory does not exits yet.
            assert not os.path.isdir(directory)
            sys.stdout.write("mkdir: %s\n" % directory)
            os.makedirs(directory)
    return errors


def setup_parser_mkdir(parser):
    parser.add_argument("dirs", nargs="+", help="Directory(s)")

command_mkdir.usage = "%(prog)s dir..."
command_mkdir.short = "Create non-existing directory (or more...)."
command_mkdir.setup_parser = setup_parser_mkdir

# -----------------------------------------------------------------------------
# SUBCOMMAND: py2to3
# -----------------------------------------------------------------------------
command_py2to4_work_around3k = True
def command_py2to3(args):
    """
    Apply '2to3' tool (Python2 to Python3 conversion tool) to Python sources.
    """
    from lib2to3.main import main
    args2 = []
    if command_py2to4_work_around3k:
        if args.no_diffs:
            args2.append("--no-diffs")
        if args.write:
            args2.append("-w")
        if args.nobackups:
            args2.append("-n")
    args2.extend(args.sources)
    sys.exit(main("lib2to3.fixes", args=args2))


def setup_parser4py2to3(parser):
    if command_py2to4_work_around3k:
        parser.add_argument("--no-diffs", action="store_true",
                          help="Don't show diffs of the refactoring")
        parser.add_argument("-w", "--write", action="store_true",
                          help="Write back modified files")
        parser.add_argument("-n", "--nobackups", action="store_true", default=False,
                          help="Don't write backups for modified files.")
    parser.add_argument("sources", nargs="+", help="Source files.")


command_py2to3.name = "2to3"
command_py2to3.usage = "%(prog)s sources..."
command_py2to3.short = "Apply python's 2to3 tool to Python sources."
command_py2to3.setup_parser = setup_parser4py2to3


# -----------------------------------------------------------------------------
# COMMAND HELPERS/UTILS:
# -----------------------------------------------------------------------------
def discover_commands():
    commands = []
    for name, func in inspect.getmembers(inspect.getmodule(toxcmd_main)):
        if name.startswith("__"):
            continue
        if name.startswith("command_") and isinstance(func, collections.Callable):
            command_name0 = name.replace("command_", "")
            command_name = getattr(func, "name", command_name0)
            commands.append(Command(command_name, func))
    return commands


class Command(object):
    def __init__(self, name, func):
        assert isinstance(name, str)
        assert isinstance(func, collections.Callable)
        self.name = name
        self.func = func
        self.parser = None

    def setup_parser(self, command_parser):
        setup_parser = getattr(self.func, "setup_parser", None)
        if setup_parser and isinstance(setup_parser, collections.Callable):
            setup_parser(command_parser)
        else:
            command_parser.add_argument("args", nargs="*")

    @property
    def usage(self):
        usage = getattr(self.func, "usage", None)
        return usage

    @property
    def short_description(self):
        short_description = getattr(self.func, "short", "")
        return short_description

    @property
    def description(self):
        return inspect.getdoc(self.func)

    def __call__(self, args):
        return self.func(args)


# -----------------------------------------------------------------------------
# MAIN-COMMAND:
# -----------------------------------------------------------------------------
def toxcmd_main(args=None):
    """Command util with subcommands for tox environments."""
    usage = "USAGE: %(prog)s [OPTIONS] COMMAND args..."
    if args is None:
        args = sys.argv[1:]

    # -- STEP: Build command-line parser.
    parser = argparse.ArgumentParser(description=inspect.getdoc(toxcmd_main),
                                     formatter_class=FORMATTER_CLASS)
    common_parser = parser.add_argument_group("Common options")
    common_parser.add_argument("--version", action="version", version=VERSION)
    subparsers = parser.add_subparsers(help="commands")
    for command in discover_commands():
        command_parser = subparsers.add_parser(command.name,
                                               usage=command.usage,
                                               description=command.description,
                                               help=command.short_description,
                                               formatter_class=FORMATTER_CLASS)
        command_parser.set_defaults(func=command)
        command.setup_parser(command_parser)
        command.parser = command_parser

    # -- STEP: Process command-line and run command.
    options = parser.parse_args(args)
    command_function = options.func
    return command_function(options)


# -----------------------------------------------------------------------------
# MAIN:
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(toxcmd_main())
