# =============================================================================
# justfile: A makefile like build script
# =============================================================================
# REQUIRES: cargo install just
# PLATFORMS: Windows, Linux, macOS, ...
# USAGE:
#   just --list
#   just <TARGET>
#   just <TARGET> <PARAM_VALUE>
#
# SEE ALSO:
#   * https://github.com/casey/just
# =============================================================================

# -- OPTION: Load environment-variables from "$HERE/.env" file (if exists)
set dotenv-load
set export := true

# -----------------------------------------------------------------------------
# CONFIG:
# -----------------------------------------------------------------------------
# NOTES:
# - PYTHON: Newer Linux may have no "python" executable, only "python3".

HERE   := justfile_directory()
PYTHON := env_var_or_default("PYTHON", "python3")
PIP_INSTALL_OPTIONS := env_var_or_default("PIP_INSTALL_OPTIONS", "--quiet")

BEHAVE_FORMATTER := env_var_or_default("BEHAVE_FORMATTER", "progress")
PYTEST_OPTIONS   := env_var_or_default("PYTEST_OPTIONS", "")

# -----------------------------------------------------------------------------
# BUILD RECIPES / TARGETS:
# -----------------------------------------------------------------------------

# DEFAULT-TARGET: Ensure that packages are installed and runs tests.
default: (_ensure-install-packages "basic") (_ensure-install-packages "testing") test

# PART=all, testing, ...
install-packages PART="all":
    @echo "INSTALL-PACKAGES: {{PART}} ..."
    {{PYTHON}} -m pip install {{PIP_INSTALL_OPTIONS}} -r py.requirements/{{PART}}.txt
    @touch "{{HERE}}/.done.install-packages.{{PART}}"

# ENSURE: Python packages are installed.
_ensure-install-packages PART="all":
    #!/usr/bin/env python3
    from subprocess import run
    from os import path
    if not path.exists("{{HERE}}/.done.install-packages.{{PART}}"):
        run("just install-packages {{PART}}", shell=True)

# -- SIMILAR: This solution requires a Bourne-like shell (may not work on: Windows).
# _ensure-install-packages PART="testing":
#   @test -e "{{HERE}}/.done.install-packages.{{PART}}" || just install-packages {{PART}}

# Run tests.
test *TESTS:
    {{PYTHON}} -m pytest {{PYTEST_OPTIONS}} {{TESTS}}

# Run behave with feature file(s) or directory(s).
behave +FEATURE_FILES="features":
    {{PYTHON}} bin/behave --format={{BEHAVE_FORMATTER}} {{FEATURE_FILES}}

# Run all behave tests.
behave-all:
    {{PYTHON}} bin/behave --format={{BEHAVE_FORMATTER}} features
    {{PYTHON}} bin/behave --format={{BEHAVE_FORMATTER}} issue.features
    {{PYTHON}} bin/behave --format={{BEHAVE_FORMATTER}} tools/test-features

# Run behave with code coverage collection(s) enabled.
coverage-behave:
    export COVERAGE_PROCESS_START="{{HERE}}/.coveragerc"
    {{PYTHON}} bin/behave --format={{BEHAVE_FORMATTER}} features
    {{PYTHON}} bin/behave --format={{BEHAVE_FORMATTER}} issue.features
    {{PYTHON}} bin/behave --format={{BEHAVE_FORMATTER}} tools/test-features
    COVERAGE_PROCESS_START=

# Run all behave tests.
test-all: test behave-all

# Determine test coverage by running the tests.
coverage:
    coverage run -m pytest
    export COVERAGE_PROCESS_START="{{HERE}}/.coveragerc"
    just coverage-behave
    COVERAGE_PROCESS_START=
    coverage combine
    coverage report
    coverage html

# coverage run -m behave --format={{BEHAVE_FORMATTER}} features
# coverage run -m behave --format={{BEHAVE_FORMATTER}} issue.features
# coverage run -m behave --format={{BEHAVE_FORMATTER}} tools/test-features

# Cleanup most parts (but leave PRECIOUS parts).
cleanup: (_ensure-install-packages "invoke")
    invoke cleanup

# Cleanup everything.
cleanup-all: (_ensure-install-packages "invoke")
    invoke cleanup.all
