# -*- coding: UTF-8 -*-
"""
Development tasks
"""

from __future__ import absolute_import, print_function
from invoke import Collection, task
from invoke.util import cd
from path import Path
import requests

# -----------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------
GHERKIN_LANGUAGES_URL = "https://raw.githubusercontent.com/cucumber/cucumber/master/gherkin/gherkin-languages.json"


# -----------------------------------------------------------------------------
# TASKS:
# -----------------------------------------------------------------------------
@task(name="update_gherkin") # TOO-LONGS: aliases=["update_gherkin_languages"])
def update_gherkin_languages(ctx):
    """Update "gherkin-languages.json" file from cucumber-repo."""
    with cd("etc/gherkin"):
        # -- BACKUP-FILE:
        gherkin_languages_file = Path("gherkin-languages.json")
        gherkin_languages_file.copy("gherkin-languages.json.SAVED")

        print('Downloading "gherkin-languages.json" from github:cucumber ...')
        download_request = requests.get(GHERKIN_LANGUAGES_URL)
        gherkin_languages_newfile = Path("gherkin-languages.json.NEW")
        assert download_request.ok
        print('Download finished: OK (size={0})'.format(len(download_request.content)))
        with open(gherkin_languages_newfile, "wb") as f:
            f.write(download_request.content)
        gherkin_languages_newfile.rename("gherkin-languages.json")

        print('Generating "i18n.py" ...')
        ctx.run("./convert_gherkin-languages.py")


# -----------------------------------------------------------------------------
# TASK HELPERS:
# -----------------------------------------------------------------------------
def print_packages(packages):
    print("PACKAGES[%d]:" % len(packages))
    for package in packages:
        package_size = package.stat().st_size
        package_time = package.stat().st_mtime
        print("  - %s  (size=%s)" % (package, package_size))


# -----------------------------------------------------------------------------
# TASK CONFIGURATION:
# -----------------------------------------------------------------------------
namespace = Collection()
namespace.add_task(update_gherkin_languages)
namespace.configure({})
