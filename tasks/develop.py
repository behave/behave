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
@task
def update_gherkin(ctx, dry_run=False):
    """Update "gherkin-languages.json" file from cucumber-repo.

    * Download "gherkin-languages.json" from cucumber repo
    * Update "gherkin-languages.json"
    * Generate "i18n.py" file from "gherkin-languages.json"
    * Update "behave/i18n.py" file (optional; not in dry-run mode)
    """
    with cd("etc/gherkin"):
        # -- BACKUP-FILE:
        gherkin_languages_file = Path("gherkin-languages.json")
        gherkin_languages_file.copy("gherkin-languages.json.SAVED")

        print('Downloading "gherkin-languages.json" from github:cucumber ...')
        download_request = requests.get(GHERKIN_LANGUAGES_URL)
        assert download_request.ok
        print('Download finished: OK (size={0})'.format(len(download_request.content)))
        with open(gherkin_languages_file, "wb") as f:
            f.write(download_request.content)

        print('Generating "i18n.py" ...')
        ctx.run("./convert_gherkin-languages.py")
        ctx.run("diff i18n.py ../../behave/i18n.py")
        if not dry_run:
            print("Updating behave/i18n.py ...")
            Path("i18n.py").move("../../behave/i18n.py")


# -----------------------------------------------------------------------------
# TASK CONFIGURATION:
# -----------------------------------------------------------------------------
# TOO-LONG: aliases=["update_gherkin_languages"])
namespace = Collection()
namespace.add_task(update_gherkin)
namespace.configure({})
