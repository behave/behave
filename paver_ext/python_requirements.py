# ============================================================================
# PAVER EXTENSION/UTILITY: Read PIP requirements files
# ============================================================================
# REQUIRES: paver >= 1.0
# REQUIRES: pkg_resources, fulfilled when setuptools or distribute is installed
# DESCRIPTION:
#   Provides some utility functions for paver.
#
# SEE ALSO:
#  * http://pypi.python.org/pypi/Paver/
#  * http://www.blueskyonmars.com/projects/paver/
# ============================================================================

# from paver.easy import error
import os.path
import pkg_resources
import sys

def error(text):
    sys.stderr.write("ERROR: %s\n" % text)
    sys.stderr.flush()

# ----------------------------------------------------------------------------
# UTILS:
# ----------------------------------------------------------------------------
def read_requirements(*filenames):
    """
    Read PIP "requirements*.txt" files.
    These files contains python package requirements.

    :param filenames:   List of requirement files to read.
    :returns: List of packages/package requirements (list-of-strings).
    """
    package_requirements = []
    for filename in filenames:
        if not os.path.exists(filename):
            error("REQUIREMENT-FILE %s not found" % filename)
            continue
        # XXX-INSTALL-REQUIRES problem w/ setup()
#       # -- NORMAL CASE:
#       with open(filename, "r") as f:
#            requirements = pkg_resources.parse_requirements(f.read())
#            package_requirements.extend(requirements)
        # -- NORMAL CASE:
        requirements_file = open(filename, "r")
        for line in requirements_file.readlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue    #< SKIP: EMPTY-LINE or COMMENT-LINE
            package_requirements.append(line)
        requirements_file.close()
    return package_requirements
