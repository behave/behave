# -*- coding: utf-8 -*-
# ============================================================================
# PAVER EXTENSION: Download dependencies with pip via requirements files
# ============================================================================
"""
A paver extension that provides pip related tasks:
  - download dependent packages
  - build a local packages index for downloaded packages

EXPECTED OPTIONS STRUCTURE:
   options.develop
       .requirements_files     -- List of requirements files to use.
       .download_dir           -- Directory for downloaded packages.

REQUIRES:
  * paver  >= 1.0.4
  * pip    >= 1.1
  * pip2pi >  0.1.1  (for localpi)

SEE ALSO:
  * http://www.blueskyonmars.com/projects/paver/
  * http://pypi.python.org/pypi/Paver/
  * http://pypi.python.org/pypi/pip/
  * http://pypi.python.org/pypi/pip2pi/
"""

from paver.easy import info, options, path, sh, task, call_task, consume_args

# ----------------------------------------------------------------------------
# TASKS:
# ----------------------------------------------------------------------------
@task
@consume_args
def download_depends(args):
    """Download all dependencies (python packages) with pip."""
    download_dir = options.develop.get("download_dir", "$HOME/.pip/downloads")
    requirements_files = None
    if args:
        info("DOWNLOAD DEPENDENCIES: %s" % ", ".join(args))
    else:
        info("DOWNLOAD ALL DEPENDENCIES: %s/" % download_dir)
        requirements_files = options.develop.requirements_files

    pip_download(download_dir, args=args, requirements_files=requirements_files)
    call_task("localpi")

@task
@consume_args
def download_deps(args):
    """Alias for: download_depends"""
    call_task("download_depends")

@task
def localpi():
    """Make local package index (used by tox)."""
    download_dir = path(options.develop.download_dir)
    if not download_dir.exists():
        call_task("download_depends")
    info("MAKE LOCAL PACKAGE-INDEX: %s/" % download_dir)
    sh("dir2pi %s" % download_dir)
    # sh("dir2pi {download_dir}".format(download_dir=download_dir))
    # -- ALTERNATIVE:
    # for reqs in requirement_files:
    #    sh("pip2pi downloads -r {requirements}".format(requirements=reqs))

# ----------------------------------------------------------------------------
# UTILS:
# ----------------------------------------------------------------------------
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
    download_dir.makedirs()
    pip_download_cmd  = "pip install --no-install --exists-action=i"
    pip_download_cmd += " --download=%s" % download_dir
    for requirement in requirements:
        # sh("{pip_download} {cmdopts} {requirement}".format(
        sh("%s %s %s" % (pip_download_cmd, cmdopts, requirement))
