# -*- coding: utf-8 -*-
# ============================================================================
# PAVER EXTENSION: Download dependencies with pip via requirements files
# ============================================================================
"""
A paver extension that provides pip related tasks:
  - download dependent packages
  - build a local packages index for downloaded packages

EXPECTED OPTIONS STRUCTURE:
   options.pip
       .requirements_files     -- List of requirements files to use.
       .download_dir           -- Directory for downloaded packages.

REQUIRES:
  * paver  >= 1.2
  * pip    >= 1.1
  * bin/make_localpi.py (script)

SEE ALSO:
  * http://www.blueskyonmars.com/projects/paver/
  * http://pypi.python.org/pypi/Paver/
  * http://pypi.python.org/pypi/pip/
"""

from paver.easy import path, sh, task, call_task, consume_args
from paver.easy import info, options, BuildFailure

# ----------------------------------------------------------------------------
# CONSTANTS:
# ----------------------------------------------------------------------------
HERE = path(__file__).dirname()
MAKE_LOCALPI_SCRIPT = HERE.joinpath("..", "bin", "make_localpi.py").normpath()


# ----------------------------------------------------------------------------
# TASKS:
# ----------------------------------------------------------------------------
@task
@consume_args
def download_deps(args):
    """Download all dependencies (python packages) with pip."""
    download_dir = options.pip.get("download_dir", "$HOME/.pip/downloads")
    requirements_files = None
    if args:
        info("DOWNLOAD DEPENDENCIES: %s" % ", ".join(args))
    else:
        info("DOWNLOAD ALL DEPENDENCIES: %s/" % download_dir)
        requirements_files = options.pip.requirements_files

    pip_download(download_dir, args=args, requirements_files=requirements_files)
    call_task("localpi")


@task
def localpi():
    """Make local python package index from download_dir contents."""
    download_dir = path(options.pip.download_dir)
    if not download_dir.exists():
        call_task("download_depends")

    require_script(MAKE_LOCALPI_SCRIPT)
    info("MAKE LOCAL PACKAGE-INDEX: %s/" % download_dir)
    sh("%s %s" % (MAKE_LOCALPI_SCRIPT, download_dir))


# ----------------------------------------------------------------------------
# UTILS:
# ----------------------------------------------------------------------------
def require_script(script_path):
    script_path = path(script_path)
    if not script_path.exists():
        message = "REQUIRE: '%s' => NOT-FOUND" % script_path
        raise BuildFailure(message)

def pip_download(download_dir, cmdopts="", args=None, requirements_files=None):
    """Download all dependencies with pip by using requirement files, etc."""
    requirements = []
    if args:
        requirements.extend(args)
    if requirements_files:
        requirements.extend([ "-r %s" % f for f in requirements_files ])
    assert requirements, "No requirements provided."

    # -- NORMAL-CASE:
    # NOTE: --exists-action option requires pip >= 1.1
    download_dir = path(download_dir)
    download_dir.makedirs_p()
    pip_download_cmd  = "pip install --use-mirrors --exists-action=i"
    pip_download_cmd += " --download=%s" % download_dir
    for requirement in requirements:
        # sh("{pip_download} {cmdopts} {requirement}".format(
        sh("%s %s %s" % (pip_download_cmd, cmdopts, requirement))
