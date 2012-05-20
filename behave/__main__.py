#!/usr/bin/env python
"""
Convenience module to use:

    python -m behave args...

"""

from __future__ import absolute_import
import sys
from .main import main

if __name__ == "__main__":
    sys.exit(main())
