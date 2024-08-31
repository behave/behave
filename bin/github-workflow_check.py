#!/usr/bin/env python3
"""
Check a github-workflow YAML file.

RELATED: JSON schema for Github Action workflows

* https://dev.to/robertobutti/vscode-how-to-check-workflow-syntax-for-github-actions-4k0o

    - https://help.github.com/en/actions/reference/workflow-syntax-for-github-actions
    - https://github.com/actions/starter-workflows/tree/master/ci
    - https://github.com/actions/starter-workflows/blob/main/ci/python-publish.yml

    REQUIRES:
        pip install check-jsonschema
        DOWNLOAD: https://github.com/SchemaStore/schemastore/blob/master/src/schemas/json/github-workflow.json
    USE: check-jsonschema --schemafile github-workflow.json_schema.txt .github/workflows/release-to-pypi.yml

* https://github.com/SchemaStore/schemastore/blob/master/src/schemas/json/github-action.json
* MAYBE: https://github.com/softprops/github-actions-schemas/blob/master/workflow.json

REQUIRES:

* pip install check-jsonschema
* pip install typer >= 0.12.5
* pip install typing-extensions

GITHUB WORKFLOW SCHEMA:

* https://github.com/SchemaStore/schemastore/blob/master/src/schemas/json/github-workflow.json
"""

from pathlib import Path
from subprocess import run
from typing import Optional
from typing_extensions import Self

import typer

# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------
HERE = Path(__file__).parent.absolute()
GITHUB_WORKFLOW_SCHEMA_URL = "https://github.com/SchemaStore/schemastore/blob/master/src/schemas/json/github-workflow.json"
GITHUB_WORKFLOW_SCHEMA_PATH = HERE/"github-workflow.json_schema"


# -----------------------------------------------------------------------------
# CLASSES:
# -----------------------------------------------------------------------------
class Verdict:
    def __init__(self, path: Path, outcome: bool, message: Optional[str] = None):
        self.path = path
        self.outcome = outcome
        self.message = message or ""

    @property
    def verdict(self):
        the_verdict = "FAILED"
        if self.outcome:
            the_verdict = "OK"
        return the_verdict

    def as_bool(self):
        return bool(self.outcome)

    def __bool__(self):
        return self.as_bool()

    def __str__(self):
        return f"{self.verdict}: {self.path}  {self.message}".strip()

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"<{class_name}: path={self.path}, verdict={self.verdict}, message='{self.message}'>"

    @classmethod
    def make_success(cls, path: Path, message: Optional[str] = None) -> Self:
        return cls(path, outcome=True, message=message)

    @classmethod
    def make_failure(cls, path: Path, message: Optional[str] = None) -> Self:
        return cls(path, outcome=False, message=message)


def workflow_check(path: Path) -> Verdict:
    schema = GITHUB_WORKFLOW_SCHEMA_PATH

    print(f"CHECK: {path} ... ")
    result = run(["check-jsonschema", f"--schemafile={schema}", f"{path}"])
    if result.returncode == 0:
        return Verdict.make_success(path)
    # -- OTHERWISE:
    return Verdict.make_failure(path)


def workflow_check_many(paths: list[Path]) -> list[Verdict]:
    verdicts = []
    for path in paths:
        verdict = workflow_check(path)
        verdicts.append(verdict)
    return verdicts


def main(paths: list[Path]) -> int:
    """
    Check github-workflow YAML file(s).

    :param paths: Paths to YAML file(s).
    :return: 0, if all checks pass. 1, otherwise
    """
    verdicts = workflow_check_many(paths)

    count_passed = 0
    count_failed = 0
    for verdict in verdicts:
        # DISABLED: print(str(verdict))
        if verdict:
            count_passed += 1
        else:
            count_failed += 1

    summary = f"SUMMARY: {len(verdicts)} files, {count_passed} passed, {count_failed} failed"
    print(summary)
    result = 1
    if count_failed == 0:
        result = 0
    return result


if __name__ == '__main__':
    typer.run(main)
