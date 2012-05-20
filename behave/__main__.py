#!/usr/bin/env python
"""
Convenience module to use:

    python -m behave args...

"""

from __future__ import absolute_import
import sys

if __name__ == "__main__":
    from .main import main
    sys.exit(main())
