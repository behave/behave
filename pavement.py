# ============================================================================
# PAVER MAKEFILE (pavement.py) -- behave
# ============================================================================
# REQUIRES: paver >= 1.0.3
# DESCRIPTION:
#   Provides platform-neutral "Makefile" for simple, project-specific tasks.
#   AVOID: setup support, because it is currently handled elsewhere.
#
# USAGE:
#   paver TASK [OPTIONS...]
#   paver help           -- Show all supported commands/tasks.
#   paver clean          -- Cleanup project workspace.
#   paver test           -- Run all tests (unittests, examples).
#
# SEE ALSO:
#  * http://pypi.python.org/pypi/Paver/
#  * http://www.blueskyonmars.com/projects/paver/
# ============================================================================

from paver.easy import *
# -- JE-DISABLED:
# from paver.setuputils import setup, install_distutils_tasks
# import paver.doctools
# -- USE EXTENSIONS: tasks, utility functions
from paver_ext.pip_download import download_depends, localpi
from paver_ext.python_checker import pychecker, pylint

# -- REQUIRED-FOR: setup, sdist, ...
# NOTE: Adds a lot more python-project related tasks.
# install_distutils_tasks()

# ----------------------------------------------------------------------------
# PROJECT CONFIGURATION (for sdist/setup mostly):
# ----------------------------------------------------------------------------
sys.path.insert(0, ".")

# ----------------------------------------------------------------------------
# TASK CONFIGURATION:
# ----------------------------------------------------------------------------
NAME = "behave"
options(
    sphinx=Bunch(
        docroot="docs",
        sourcedir=".",
        builddir="../build/docs"
    ),
    minilib=Bunch(
        extra_files=[ 'doctools', 'virtual' ]
    ),
    behave_test=Bunch(
        default_args=[ "tools/test-features/" ]
    ),
    pychecker = Bunch(
        default_args=NAME
    ),
    pylint = Bunch(
        default_args=NAME
    ),
    develop=Bunch(
        requirements_files=[
            "requirements.txt",
            "requirements-develop.txt",
        ],
        download_dir="downloads",
    ),
)

# ----------------------------------------------------------------------------
# TASKS:
# ----------------------------------------------------------------------------
@task
@consume_args
def docs(args):
    """Generate the documentation: html, pdf, ... (default: html)"""
    builders = args
    if not builders:
        builders = [ "html" ]
    for builder in builders:
        sphinx_build(builder)

@task
def linkcheck():
    """Check hyperlinks in documentation."""
    sphinx_build("linkcheck")


# ----------------------------------------------------------------------------
# TASK: test
# ----------------------------------------------------------------------------
@task
@consume_args
def test(args):
    """Execute all tests (unittests, feature tests)."""
    call_task("unittest")
    call_task("feature_test")

@task
@consume_args
def unittest(args):
    """Execute all unittests w/ nosetest runner."""
    cmdline = ""
    if args:
        cmdline = " ".join(args)
    nosetests(cmdline)

@task
@consume_args
def feature_test(args):
    """Execute all feature tests w/ behave."""
    if not args:
        # args = [ "features" ]
        args = options.behave_test.default_args
    excluded_tags = "--tags=-xfail"
    cmdopts = excluded_tags
    for arg in args:
        behave(arg, cmdopts)


# ----------------------------------------------------------------------------
# TASK: test coverage
# ----------------------------------------------------------------------------
@task
def coverage_report():
    """Generate coverage report from collected coverage data."""
    sh("coverage combine")
    sh("coverage report")
    sh("coverage html")
    info("WRITTEN TO: build/coverage.html/")
    # -- DISABLED: sh("coverage xml")

@task
@consume_args
def coverage(args):
    """Run unittests and collect coverage, then generate report."""
    unittests = []
    feature_tests = []

    # -- STEP: Select unittests and feature-tests (if any).
    for arg in args:
        if arg.startswith("test"):
            unittests.append(arg)
        elif arg.startswith("tools"):
            feature_tests.append(arg)
        else:
            unittests.append(arg)
            feature_tests.append(arg)

    # -- STEP: Check if all tests should be run (normally: no args provided).
    should_always_run = not unittests and not feature_tests
    if should_always_run:
        feature_tests = list(options.behave_test.default_args)

    # -- STEP: Run unittests.
    if unittests or should_always_run:
        nosetests_coverage_run2(" ".join(unittests))

    # -- STEP: Run feature-tests.
    if feature_tests or should_always_run:
        feature_tests.insert(0, "--tags=-xfail")
        behave = path("bin/behave").normpath()
        coverage_run("{behave} {args}".format(
                behave=behave, args=" ".join(feature_tests)))
        call_task("coverage_report")


# ----------------------------------------------------------------------------
# TASK: bump_version
# ----------------------------------------------------------------------------
@task
def bump_version(info, error):
    """Update VERSION.txt"""
    try:
        from behave import __version__ as VERSION
        info("VERSION: %s" % VERSION)
        file_ = open("VERSION.txt", "w+")
        file_.write("%s\n" % VERSION)
        file_.close()
    except StandardError, e:
        error("Update VERSION.txt FAILED: %s" % e)


# ----------------------------------------------------------------------------
# TASK: clean
# ----------------------------------------------------------------------------
@task
def clean():
    """Cleanup the project workspace."""

    # -- STEP: Remove build directories.
    path("build").rmtree()
    path("dist").rmtree()
    path(".tox").rmtree()

    # -- STEP: Remove temporary directory subtrees.
    patterns = [
        "*.egg-info",
        "__pycache__",
    ]
    for pattern in patterns:
        dirs = path(".").walkdirs(pattern, errors="ignore")
        for d in dirs:
            d.rmtree()

    # -- STEP: Remove files.
    path(".coverage").remove()
    path("paver-minilib.zip").remove()

    # -- STEP: Remove temporary files.
    patterns = [
        "*.pyc", "*.pyo", "*.bak", "*.log", "*.tmp",
        ".coverage", ".coverage.*",
        "pylint_*.txt", "pychecker_*.txt",
        ".DS_Store", "*.~*~",   #< MACOSX
    ]
    for pattern in patterns:
        files = path(".").walkfiles(pattern)
        for f in files:
            f.remove()

@task
def clean_all():
    """Clean everything.."""
    # -- ORDERING: Is important
    path(".packages").rmtree()

    # -- MORE: Use normal cleanings, too.
    call_task("clean")

# ----------------------------------------------------------------------------
# PLATFORM-SPECIFIC TASKS: win32
# ----------------------------------------------------------------------------
#if sys.platform == "win32":
#    @task
#    @consume_args
#    def py2exe(args):
#        """Run py2exe to build a win32 executable."""
#        cmdline = " ".join(args)
#        python("setup_py2exe.py py2exe %s" % cmdline)
#
# ----------------------------------------------------------------------------
# UTILS:
# ----------------------------------------------------------------------------
BEHAVE   = path("bin/behave").normpath()

def python(cmdline, cwd="."):
    """Execute a python script by using the current python interpreter."""
    return sh("{python} {cmd}".format(python=sys.executable, cmd=cmdline),
                cwd=cwd)

def coverage_run(cmdline):
    return sh("coverage run {cmdline}".format(cmdline=cmdline))
        # ignore_error=True)   #< Show coverage-report even if tests fail.

def nosetests(cmdline, cmdopts=""):
    """Run nosetest command"""
    return sh("nosetests {options} {args}".format(options=cmdopts, args=cmdline))

def nosetests_coverage_run(cmdline, cmdopts=""):
    """Collect coverage w/ nose-builtin coverage plugin."""
    cmdopts += " --with-coverage --cover-package={package}".format(package=NAME)
    return nosetests(cmdline, cmdopts)

def nosetests_coverage_run2(cmdline, cmdopts=""):
    """Collect coverage w/ extra nose-cov plugin."""
    cmdopts += " --with-cov --cov={package}".format(package=NAME)
    return nosetests(cmdline, cmdopts)

def behave(cmdline, cmdopts=""):
    """Run behave command"""
    return sh("{behave} {options} {args}".format(
                behave=BEHAVE, options=cmdopts, args=cmdline))

def sphinx_build(builder="html", cmdopts=""):
    sourcedir = options.sphinx.sourcedir
    destdir   = options.sphinx.builddir
    cmd = "sphinx-build {opts} -b {builder} {sourcedir} {destdir}/{builder}"\
            .format(builder=builder, sourcedir=sourcedir,
                    destdir=destdir, opts=cmdopts)
    sh(cmd, cwd=options.sphinx.docroot)
