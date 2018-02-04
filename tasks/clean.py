# -*- coding: UTF-8 -*-
"""
Provides cleanup tasks for this project.
Mostly reuses tasks from "invoke_tasklet_clean".
"""

from __future__ import absolute_import
from ._tasklet_cleanup import cleanup_tasks


# -----------------------------------------------------------------------------
# TASKS:
# -----------------------------------------------------------------------------
# INHERITED-FROM: _invoke_tasklet_clean
# pylint: disable=unused-import
from ._tasklet_cleanup import clean, clean_all, clean_python, namespace


# -- EXTENSTION-POINT: CLEANUP TASKS (called by: "clean" task):
cleanup_tasks.add_task(clean_python)


# -----------------------------------------------------------------------------
# TASK CONFIGURATION:
# -----------------------------------------------------------------------------
# namespace = Collection(clean, clean_all)
# namespace.configure({
#     "clean": {
#         "directories": [],
#         "files": [
#             "*.bak", "*.log", "*.tmp",
#             "**/.DS_Store", "**/*.~*~",     # -- MACOSX
#         ],
#         "extra_directories": [],
#         "extra_files": [],
#     },
#     "clean_all": {
#         "directories": [".venv*", ".tox", "downloads", "tmp"],
#         "files": [],
#         "extra_directories": [],
#         "extra_files": [],
#     },
# })
#
# -----------------------------------------------------------------------------
# TASK CONFIGURATION HELPERS: Can be used from other task modules
# -----------------------------------------------------------------------------
# def config_add_cleanup_dirs(directories):
#     cleanup_directories = namespace._configuration["clean"]["directories"]
#     cleanup_directories.extend(directories)
#
# def config_add_cleanup_files(files):
#     cleanup_files = namespace._configuration["clean"]["files"]
#     cleanup_files.extend(files)
