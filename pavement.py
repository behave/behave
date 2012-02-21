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
# -- JE-DISABLED: from paver.setuputils import setup, install_distutils_tasks
# -- JE-DISABLED: import paver.doctools
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
options(
    sphinx=Bunch(
        # docroot=".",
        # sourcedir="docs",
        builddir="../build/docs"
    ),
    minilib=Bunch(
        extra_files=[ 'doctools', 'virtual' ]
    ),
    test=Bunch(
        default_args=[ "features/" ]
    ),
    pychecker = Bunch(
        default_dirs=[ "behave" ]
    ),
    pylint = Bunch(
        default_dirs=[ "behave" ]
    )
)

# ----------------------------------------------------------------------------
# TASKS:
# ----------------------------------------------------------------------------
@task
def init():
    """Initialze workspace."""
    pass

@task
def docs_html():
    """Generate the HTML-based documentation."""
    call_task("prepare_docs")
    sphinx_build("html")

@task
def docs_pdf():
    """Generate the PDF-based documentation."""
    sphinx_build("pdf")
    # sh("make -C docs pdf")

@task
def docs():
    """Generate the documentation."""
    call_task("docs_html")


# ----------------------------------------------------------------------------
# TASK: test
# ----------------------------------------------------------------------------
@task
@consume_args
def test(args):
    """Execute all tests"""
    if not args:
        # args = [ "features" ]
        args = options.test.default_args
    for arg in args:
        behave(arg)

# ----------------------------------------------------------------------------
# TASK: test coverage
# ----------------------------------------------------------------------------
#@task
#def coverage_report():
#    """Generate coverage report from collected coverage data."""
#    sh("coverage combine")
#    sh("coverage report")
#    sh("coverage html")
#    # -- DISABLED: sh("coverage xml")
#
#@task
#@consume_args
#def coverage(args):
#    """Execute all tests to collect code-coverage data, generate report."""
#    tests = " ".join(args)
#    sh("coverage run bin/pytest.py --cov=%s %s" % (NAME, tests),
#       ignore_error=True)   #< Show coverage-report even if tests fail.
#    call_task("coverage_report")
#

# ----------------------------------------------------------------------------
# TASK: pychecker, pylint
# ----------------------------------------------------------------------------
@task
@consume_args
def pylint(args):
    """Run pylint on sources."""
    if not args:
        args = []
        for dir_ in options.pylint.default_dirs:
            args.extend(path(dir_).walkfiles("*.py"))
    cmdline = " ".join(args)
    sh("pylint --rcfile=.pylintrc %s" % cmdline, ignore_error=True)
    # XXX-JE-TODO

@task
@consume_args
def pychecker(args):
    """Run pychecker on sources."""
    if not args:
        args = []
        for dir_ in options.pylint.default_dirs:
            args.extend(path(dir_).walkfiles("*.py"))
    for file_ in args:
        cmdline = file_
        sh("pychecker --config=.pycheckrc %s" % cmdline, ignore_error=True)

# ----------------------------------------------------------------------------
# TASK: bump_version
# ----------------------------------------------------------------------------
@task
def bump_version(info, error):
    """Update VERSION.txt"""
    try:
        from behave.version import VERSION
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
        "*.output", "*.diff",   #< RAVEN
        ".DS_Store", "*.~*~",   #< MACOSX
    ]
    for pattern in patterns:
        files = path(".").walkfiles(pattern)
        for f in files:
            f.remove()


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
BEHAVE = path("bin/behave").normpath()

def python(cmdline, cwd="."):
    """Execute a python script by using the current python interpreter."""
    return sh("%s %s" % (sys.executable, cmdline), cwd=cwd)

def behave(cmdline, options=""):
    """
    Run behave command
    """
    # XXX return python("{behave} {options} {args}".format(
    return sh("{behave} {options} {args}".format(
                behave=BEHAVE, options=options, args=cmdline))

def sphinx_build(builder="html"):
    # sourcedir = "docs"
    destdir   = "../build/docs"
    command = "sphinx-build -b {builder} . {destdir}/{builder}".format(
                builder=builder, destdir=destdir)
    sh(command, cwd="docs")
