# -*- coding -*-
"""
Provides some command utility functions.

TODO:
  matcher that ignores empty lines and whitespace and has contains comparison
"""

from __future__ import print_function, unicode_literals
# from behave4cmd.steputil import ensure_attribute_exists
# import shutil
import os.path
import codecs
# try:
#     import io
# except ImportError:
#     # -- FOR: python2.5
#     import codecs as io

# -----------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------
# HERE     = os.path.dirname(__file__)
# WORKDIR  = os.path.join(HERE, "..", "__WORKDIR__")
# # -- XXX-SHOULD-BE:
# WORKDIR  = os.path.join(os.getcwd(), "__WORKDIR__")
# WORKDIR  = os.path.abspath(WORKDIR)


# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def realpath_with_context(path, context):
    """
    Convert a path into its realpath:

      * For relative path: use :attr:`context.workdir` as root directory
      * For absolute path: Pass-through without any changes.

    :param path: Filepath to convert (as string).
    :param context: Behave context object (with :attr:`context.workdir`)
    :return: Converted path.
    """
    if not os.path.isabs(path):
        # XXX ensure_workdir_exists(context)
        assert context.workdir
        path = os.path.join(context.workdir, os.path.normpath(path))
    return path

def posixpath_normpath(pathname):
    """
    Convert path into POSIX path:

      * Normalize path
      * Replace backslash with slash

    :param pathname: Pathname (as string)
    :return: Normalized POSIX path.
    """
    backslash = '\\'
    pathname2 = os.path.normpath(pathname) or "."
    if backslash in pathname2:
        pathname2 = pathname2.replace(backslash, '/')
    return pathname2

def read_file_contents(filename, context=None, encoding=None):
    filename_ = realpath_with_context(filename, context)
    assert os.path.exists(filename_)
    with open(filename_, "r") as file_:
        file_contents = file_.read()
    return file_contents

# def create_new_workdir(context):
#     ensure_attribute_exists(context, "workdir", default=WORKDIR)
#     if os.path.exists(context.workdir):
#         shutil.rmtree(context.workdir, ignore_errors=True)
#     ensure_workdir_exists(context)

def create_textfile_with_contents(filename, contents, encoding='utf-8'):
    """
    Creates a textual file with the provided contents in the workdir.
    Overwrites an existing file.
    """
    ensure_directory_exists(os.path.dirname(filename))
    if os.path.exists(filename):
        os.remove(filename)
    outstream = codecs.open(filename, "w", encoding)
    outstream.write(contents)
    if contents and not contents.endswith("\n"):
        outstream.write("\n")
    outstream.flush()
    outstream.close()
    assert os.path.exists(filename), "ENSURE file exists: %s" % filename


def ensure_file_exists(filename, context=None):
    real_filename = filename
    if context:
        real_filename = realpath_with_context(filename, context)
    if not os.path.exists(real_filename):
        create_textfile_with_contents(real_filename, "")
    assert os.path.exists(real_filename), "ENSURE file exists: %s" % filename

def ensure_directory_exists(dirname, context=None):
    """
    Ensures that a directory exits.
    If it does not exist, it is automatically created.
    """
    real_dirname = dirname
    if context:
        real_dirname = realpath_with_context(dirname, context)
    if not os.path.exists(real_dirname):
        os.makedirs(real_dirname)
    assert os.path.exists(real_dirname), "ENSURE dir exists: %s" % dirname
    assert os.path.isdir(real_dirname),  "ENSURE isa dir: %s" % dirname

# def ensure_workdir_exists(context):
#     """
#     Ensures that the work directory exists.
#     In addition, the location of the workdir is stored as attribute in
#     the context object.
#     """
#     ensure_attribute_exists(context, "workdir", default=WORKDIR)
#     # if not context.workdir:
#     #     context.workdir = os.path.abspath(WORKDIR)
#     ensure_directory_exists(context.workdir)
