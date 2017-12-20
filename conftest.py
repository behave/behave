# -*- coding: UTF-8 -*-
"""
Configure pytest environment.
Add project-specific information.

.. seealso::
    * https://github.com/pytest-dev/pytest-html
"""

import behave
import pytest

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

