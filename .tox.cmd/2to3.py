#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Same as `2to3` (Python2 to Python3 conversion tool).
"""

import sys
from lib2to3.main import main

sys.exit(main("lib2to3.fixes"))
