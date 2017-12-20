# -*- coding -*-
"""
Provides some command utility functions.

TODO:
  matcher that ignores empty lines and whitespace and has contains comparison
"""

from __future__ import absolute_import, print_function
import os.path
import sys
import codecs


# -----------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------
# HERE, WORKDIR: see "__setup.py"


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


def ensure_makedirs(directory, max_iterations=3):
    # -- SPORADIC-ERRORS: WindowsError: [Error 5] Access denied: '...'
    iteration = 0
    exception_text = None
    for iteration in range(max_iterations):
        try:
            os.makedirs(directory)
        except OSError as e:
            if iteration >= max_iterations: # XXX-BAD: Never occurs
                raise
            else:
                exception_text = "%s:%s" % (e.__class__.__name__, e)

        if os.path.isdir(directory):
            return

    assert os.path.isdir(directory), \
        "FAILED: ensure_makedirs(%r) (after %s iterations):\n%s" % \
        (directory, max_iterations, exception_text)


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
    """Ensures that a directory exits.
    If it does not exist, it is automatically created.
    """
    real_dirname = dirname
    if context:
        real_dirname = realpath_with_context(dirname, context)
    if not os.path.exists(real_dirname):
        mas_iterations = 2
        if sys.platform.startswith("win"):
            mas_iterations = 10
        ensure_makedirs(real_dirname, mas_iterations)

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
