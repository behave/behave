#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Convenience module to use:

    python -m behave args...

"""

from __future__ import absolute_import
import sys
from .main import main, DISABLE_MULTI_FORMATTERS

if __name__ == "__main__":
    sys.exit(main())
