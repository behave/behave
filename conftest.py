# -*- coding: UTF-8 -*-
"""
Configure pytest environment.
Add project-specific information.

.. seealso::
    * https://github.com/pytest-dev/pytest-html
"""

import behave
import pytest


# ---------------------------------------------------------------------------
# PYTEST FIXTURES:
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _annotate_environment(request):
    """Add project-specific information to test-run environment:

    * behave.version

    NOTE: autouse: Fixture is automatically used when test-module is imported.
    """
    # -- USEFULL FOR: pytest --html=report.html ...
    environment = getattr(request.config, "_environment", None)
    if environment:
        # -- PROVIDED-BY: pytest-html
        behave_version = behave.__version__
        environment.append(("behave", behave_version))

_pytest_version = pytest.__version__
if _pytest_version >= "5.0":
    # -- SUPPORTED SINCE: pytest 5.0
    @pytest.fixture(scope="session", autouse=True)
    def log_global_env_facts(record_testsuite_property):
        # SEE: https://docs.pytest.org/en/latest/usage.html
        behave_version = behave.__version__
        record_testsuite_property("BEHAVE_VERSION", behave_version)

