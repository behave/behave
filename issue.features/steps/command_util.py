# -*- coding -*-
"""
Provides some command utility functions.

TODO:
  matcher that ignores empty lines and whitespace and has contains comparison
"""

import os.path

# -----------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------
HERE    = os.path.dirname(__file__)
WORKDIR = os.path.join(HERE, "..", "..", "__WORKDIR__")

# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def ensure_directory_exists(dirname):
    """
    Ensures that a directory exits.
    If it does not exist, it is automatically created.
    """
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    assert os.path.exists(dirname)
    assert os.path.isdir(dirname)

def ensure_context_resource_exists(context, name, default_value=None):
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
    ensure_context_resource_exists(context, "workdir", None)
    if not context.workdir:
        context.workdir = os.path.abspath(WORKDIR)
    ensure_directory_exists(context.workdir)


def create_textfile_with_contents(filename, contents):
    """
    Creates a textual file with the provided contents in the workdir.
    Overwrites an existing file.
    """
    ensure_directory_exists(os.path.dirname(filename))
    if os.path.exists(filename):
        os.remove(filename)
    outstream = open(filename, "w")
    outstream.write(contents)
    if not contents.endswith("\n"):
        outstream.write("\n")
    outstream.flush()
    outstream.close()
    assert os.path.exists(filename)

def text_remove_empty_lines(text):
    """
    Whitespace normalization:
      - Strip empty lines
      - Strip trailing whitespace
    """
    lines = [ line.rstrip()  for line in text.splitlines()  if line.strip() ]
    return "\n".join(lines)

def text_normalize(text):
    """
    Whitespace normalization:
      - Strip empty lines
      - Strip leading whitespace  in a line
      - Strip trailing whitespace in a line
      - Normalize line endings
    """
    lines = [ line.strip()  for line in text.splitlines()  if line.strip() ]
    return "\n".join(lines)

def posixpath_normpath(pathname):
    """
    Convert path into POSIX path:
      - Normalize path
      - Replace backslash with slash
    """
    backslash = '\\'
    pathname = os.path.normpath(pathname)
    if backslash in pathname:
        pathname = pathname.replace(backslash, '/')
    return pathname
