# -*- coding: UTF-8 -*-
"""
Provides cleanup tasks for invoke build scripts.

clean task: Add Additional Directories and Files to be removed
-------------------------------------------------------------------------------

Create an invoke configuration file (YAML of JSON) with the additional
configuration data:

.. code-block:: yaml

    # -- FILE: invoke.yaml
    # USE: clean.directories, clean.files to override current configuration.
    clean:
        extra_directories:
            - **/tmp/
        extra_files:
            - **/*.log
            - **/*.bak


Registration of Cleanup Tasks
------------------------------

Other task modules often have an own cleanup task to recover the clean state.
The :meth:`clean` task, that is provided here, supports the registration
of additional cleanup tasks. Therefore, when the :meth:`clean` task is executed,
all registered cleanup tasks will be executed.

EXAMPLE::

    # -- FILE: tasks/docs.py
    from __future__ import absolute_import
    from invoke import task, Collection
    from .clean import cleanup_tasks, cleanup_dirs

    @task
    def clean(ctx, dry_run=False):
        "Cleanup generated documentation artifacts."
        cleanup_dirs(["build/docs"])

    namespace = Collection(clean)
    ...

    # -- REGISTER CLEANUP TASK:
    cleanup_tasks.add_task(clean, "clean_docs")
    cleanup_tasks.configure(namespace.configuration())
"""

from __future__ import absolute_import
from invoke import task, Collection
from invoke.executor import Executor
from invoke.exceptions import Failure
import os.path
import sys
import shutil
from pathlib import Path
import six

# -----------------------------------------------------------------------------
# TASKS:
# -----------------------------------------------------------------------------
@task
def clean(ctx, dry_run=False):
    """Cleanup temporary dirs/files to regain a clean state."""
    # -- VARIATION-POINT 1: Allow user to override in configuration-file
    directories = ctx.clean.directories
    files = ctx.clean.files

    # -- VARIATION-POINT 2: Allow user to add more files/dirs to be removed.
    extra_directories = ctx.clean.extra_directories or []
    extra_files = ctx.clean.extra_files or []
    if extra_directories:
        directories.extend(extra_directories)
    if extra_files:
        files.extend(extra_files)

    # -- PERFORM CLEANUP:
    execute_cleanup_tasks(ctx, cleanup_tasks, dry_run=dry_run)
    cleanup_dirs(directories, dry_run=dry_run)
    cleanup_files(files, dry_run=dry_run)


@task(name="clean-all", aliases=("distclean",))
def clean_all(ctx, dry_run=False):
    """Clean up everything, even the precious stuff.
    NOTE: clean task is executed first.
    """
    # print("clean-all:")
    # BAD: clean(ctx, dry_run=dry_run)
    cleanup_dirs(ctx.clean_all.directories or [], dry_run=dry_run)
    cleanup_files(ctx.clean_all.files or [], dry_run=dry_run)
    clean(ctx, dry_run=dry_run)


@task
def clean_python(ctx, dry_run=False):
    """Cleanup python related files/dirs: *.pyc, *.pyo, ..."""
    # MAYBE NOT: "**/__pycache__"
    cleanup_dirs(["build", "dist", "*.egg-info", "**/__pycache__"],
                 dry_run=dry_run)
    if not dry_run:
        ctx.run("py.cleanup")
    cleanup_files(["**/*.pyc", "**/*.pyo", "**/*$py.class"], dry_run=dry_run)


# -----------------------------------------------------------------------------
# CLEANUP UTILITIES:
# -----------------------------------------------------------------------------
def execute_cleanup_tasks(ctx, cleanup_tasks, dry_run=False):
    """Execute several cleanup tasks as part of the cleanup.

    :param ctx:             Context object for the tasks.
    :param cleanup_tasks:   Collection of cleanup tasks (as Collection).
    :param dry_run:         Indicates dry-run mode (bool)
    """
    executor = Executor(cleanup_tasks, ctx.config)
    for cleanup_task in cleanup_tasks.tasks:
        print("CLEANUP TASK: %s" % cleanup_task)
        executor.execute((cleanup_task, dict(dry_run=dry_run)))


def cleanup_dirs(patterns, dry_run=False, workdir="."):
    """Remove directories (and their contents) recursively.
    Skips removal if directories does not exist.

    :param patterns:    Directory name patterns, like "**/tmp*" (as list).
    :param dry_run:     Dry-run mode indicator (as bool).
    :param workdir:     Current work directory (default=".")
    """
    current_dir = Path(workdir)
    python_basedir = str(Path(sys.executable).parent.parent)
    warn2_counter = 0
    for dir_pattern in patterns:
        for directory in current_dir.glob(dir_pattern):
            if sys.executable.startswith(str(directory.absolute())):
                print("SKIP-SUICIDE: '%s' contains current python executable" % directory)
                continue
            elif str(directory.absolute()).startswith(python_basedir):
                # -- PROTECT CURRENTLY USED VIRTUAL ENVIRONMENT:
                if warn2_counter <= 4:
                    python_basedir2 = os.path.relpath(python_basedir)
                    print("SKIP-SUICIDE: '%s'" % directory)
                warn2_counter += 1
                continue

            if dry_run:
                print("RMTREE: %s (dry-run)" % directory)
            else:
                print("RMTREE: %s" % directory)
                shutil.rmtree(str(directory))

def cleanup_files(patterns, dry_run=False, workdir="."):
    """Remove files or files selected by file patterns.
    Skips removal if file does not exist.

    :param patterns:    File patterns, like "**/*.pyc" (as list).
    :param dry_run:     Dry-run mode indicator (as bool).
    :param workdir:     Current work directory (default=".")
    """
    current_dir = Path(workdir)
    python_basedir = str(Path(sys.executable).parent.parent)
    error_message = None
    error_count = 0
    for file_pattern in patterns:
        for file_ in current_dir.glob(file_pattern):
            if str(file_.absolute()).startswith(python_basedir):
                # -- PROTECT CURRENTLY USED VIRTUAL ENVIRONMENT:
                continue

            if dry_run:
                print("REMOVE: %s (dry-run)" % file_)
            else:
                print("REMOVE: %s" % file_)
                try:
                    file_.unlink()
                except os.error as e:
                    message = "%s: %s" % (e.__class__.__name__, e)
                    print(message + " basedir: "+ python_basedir)
                    error_count += 1
                    if not error_message:
                        error_message = message
    if False and error_message:
        class CleanupError(RuntimeError): pass
        raise CleanupError(error_message)


# -----------------------------------------------------------------------------
# TASK CONFIGURATION:
# -----------------------------------------------------------------------------
namespace = Collection(clean, clean_all)
namespace.configure({
    "clean": {
        "directories": [],
        "files": [
            "*.bak", "*.log", "*.tmp",
            "**/.DS_Store", "**/*.~*~",     # -- MACOSX
        ],
        "extra_directories": [],
        "extra_files": [],
    },
    "clean_all": {
        "directories": [".venv*", ".tox", "downloads", "tmp"],
        "files": [],
    },
})

# -- SUPPORT ADDITIONAL CLEANUP TASKS:
cleanup_tasks = Collection("cleanup_tasks")
cleanup_tasks.add_task(clean_python)
# NOT-NEEDED HERE:
# cleanup_tasks.configure(namespace.configuration())

# -----------------------------------------------------------------------------
# TASK CONFIGURATION HELPERS: Can be used from other task modules
# -----------------------------------------------------------------------------
def config_add_cleanup_dirs(directories):
    cleanup_directories = namespace._configuration["clean"]["directories"]
    cleanup_directories.extend(directories)

def config_add_cleanup_files(files):
    cleanup_files = namespace._configuration["clean"]["files"]
    cleanup_files.extend(files)

