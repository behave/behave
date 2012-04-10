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

from paver.easy import info, options, path, sh, task, call_task

# ----------------------------------------------------------------------------
# TASKS:
# ----------------------------------------------------------------------------
@task
def download_depends():
    """Download all dependencies (python packages) with pip."""
    download_dir = options.develop.download_dir
    info("DOWNLOAD ALL DEPENDENCIES: {0}/".format(download_dir))
    pip_download(download_dir,
                requirements_files=options.develop.requirements_files)

@task
def localpi():
    """Make local package index (used by tox)."""
    download_dir = path(options.develop.download_dir)
    if not download_dir.exists():
        call_task("download_depends")
    info("MAKE LOCAL PACKAGE-INDEX: {0}/".format(download_dir))
    sh("dir2pi {download_dir}".format(download_dir=download_dir))
    # -- ALTERNATIVE:
    # for reqs in requirement_files:
    #    sh("pip2pi downloads -r {requirements}".format(requirements=reqs))

# ----------------------------------------------------------------------------
# UTILS:
# ----------------------------------------------------------------------------
def pip_download(download_dir, cmdopts="", requirements_files=None):
    """Download all dependencies with pip by using requirement files, etc."""
    if not cmdopts and not requirements_files:
        assert False, "Neither requirement_files nor cmdopts provided."

    # -- NORMAL-CASE:
    # NOTE: --exists-action option requires pip >= 1.1
    download_dir = path(download_dir)
    download_dir.makedirs()
    pip_download_cmd  = "pip install --no-install --exists-action=i"
    pip_download_cmd += " --download={0}".format(download_dir)

    if requirements_files:
        # -- WITH REQUIREMENT FILES:
        for requirements_file in requirements_files:
            sh("{pip_download} {cmdopts} -r {requirements_file}"\
                .format(pip_download=pip_download_cmd, cmdopts=cmdopts,
                        requirements_file=requirements_file))
    else:
        # -- NO REQUIREMENT FILES: Requirement in cmdopts, ala: argparse>=1.2
        assert cmdopts
        sh("{pip_download} {cmdopts}".format(
            pip_download=pip_download_cmd, cmdopts=cmdopts))
