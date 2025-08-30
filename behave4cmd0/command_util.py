"""
Provides some command utility functions.

TODO:
  matcher that ignores empty lines and whitespace and has contains comparison
"""

from behave4cmd0 import pathutil
from behave4cmd0.__setup import TOP, TOPA
import os.path
import sys
import shutil
import time
import tempfile
from fnmatch import fnmatch

# -----------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------
# HERE    = os.path.dirname(__file__)
# TOP     = os.path.join(HERE, "..")
# TOPA    = os.path.abspath(TOP)
WORKDIR = os.path.join(TOP, "__WORKDIR__")


# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def workdir_save_coverage_files(workdir, destdir=None):
    assert os.path.isdir(workdir)
    if not destdir:
        destdir = TOPA
    if os.path.abspath(workdir) == os.path.abspath(destdir):
        return  # -- SKIP: Source directory is destination directory (SAME).

    for fname in os.listdir(workdir):
        if fnmatch(fname, ".coverage.*"):
            # -- MOVE COVERAGE FILES:
            sourcename = os.path.join(workdir, fname)
            shutil.move(sourcename, destdir)

# def ensure_directory_exists(dirname):
#     """
#     Ensures that a directory exits.
#     If it does not exist, it is automatically created.
#     """
#     if not os.path.exists(dirname):
#         os.makedirs(dirname)
#     assert os.path.exists(dirname)
#     assert os.path.isdir(dirname)

def ensure_context_attribute_exists(context, name, default_value=None):
    """
    Ensure a behave resource exists as attribute in the behave context.
    If this is not the case, the attribute is created by using the default_value.
    """
    if not hasattr(context, name):
        setattr(context, name, default_value)

def ensure_workdir_exists(context):
    """
    Ensures that the work directory exists.
    In addition, the location of the workdir is stored as attribute in
    the context object.
    """
    ensure_context_attribute_exists(context, "workdir", None)
    if not context.workdir:
        context.workdir = os.path.abspath(WORKDIR)
    pathutil.ensure_directory_exists(context.workdir)

def ensure_workdir_not_exists(context):
    """Ensures that the work directory does not exist."""
    ensure_context_attribute_exists(context, "workdir", None)
    if not context.workdir or not os.path.exists(context.workdir):
        return

    # -- WORKDIR EXISTS: Remove this directory
    orig_directory = real_directory = context.workdir
    context.workdir = None
    # -- WAS:
    # renamed_directory = tempfile.mktemp(prefix=os.path.basename(real_directory),
    #                                     suffix="_DEAD",
    #                                     dir=os.path.dirname(real_directory) or ".")
    real_directory_basename = os.path.basename(real_directory)
    temporary_directory = tempfile.mkdtemp(prefix=real_directory_basename,
                                           suffix="_DEAD")
    renamed_directory = os.path.join(temporary_directory, real_directory_basename)
    try:
        # -- MOVE-DIRECTORY: May fail if on different filesystems
        os.rename(real_directory, renamed_directory)
        real_directory = renamed_directory
    except OSError:
        pass

    max_iterations = 2
    if sys.platform.startswith("win"):
        max_iterations = 15

    # -- REMOVE DIRECTORY:
    for iteration in range(max_iterations):
        if not os.path.exists(real_directory):
            if iteration > 1:
                print("REMOVE-WORKDIR after %s iterations" % (iteration+1))
            break
        shutil.rmtree(real_directory, ignore_errors=True)
        time.sleep(0.5)
    shutil.rmtree(temporary_directory, ignore_errors=True)
    assert not os.path.isdir(real_directory), "ENSURE not-isa dir: %s" % real_directory
    assert not os.path.exists(real_directory), "ENSURE dir not-exists: %s" % real_directory
    assert not os.path.isdir(orig_directory), "ENSURE not-isa dir: %s" % orig_directory


# def create_textfile_with_contents(filename, contents):
#     """
#     Creates a textual file with the provided contents in the workdir.
#     Overwrites an existing file.
#     """
#     ensure_directory_exists(os.path.dirname(filename))
#     if os.path.exists(filename):
#         os.remove(filename)
#     outstream = open(filename, "w")
#     outstream.write(contents)
#     if not contents.endswith("\n"):
#         outstream.write("\n")
#     outstream.flush()
#     outstream.close()
#     assert os.path.exists(filename)

# def text_remove_empty_lines(text):
#     """
#     Whitespace normalization:
#       - Strip empty lines
#       - Strip trailing whitespace
#     """
#     lines = [ line.rstrip()  for line in text.splitlines()  if line.strip() ]
#     return "\n".join(lines)
#
# def text_normalize(text):
#     """
#     Whitespace normalization:
#       - Strip empty lines
#       - Strip leading whitespace  in a line
#       - Strip trailing whitespace in a line
#       - Normalize line endings
#     """
#     lines = [ line.strip()  for line in text.splitlines()  if line.strip() ]
#     return "\n".join(lines)

# def posixpath_normpath(pathname):
#     """
#     Convert path into POSIX path:
#       - Normalize path
#       - Replace backslash with slash
#     """
#     backslash = '\\'
#     pathname = os.path.normpath(pathname)
#     if backslash in pathname:
#         pathname = pathname.replace(backslash, '/')
#     return pathname
