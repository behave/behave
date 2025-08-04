# -*- coding: UTF-8 -*-
# REQUIRES: Python >= 3.5

from __future__ import absolute_import
import sys

python_version = sys.version_info[:2]
if python_version >= (3, 5):
    import _async_steps35  # noqa: F401
