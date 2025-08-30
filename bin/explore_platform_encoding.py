#!/usr/bin/env python3
"""
Explore encoding settings on a platform.
"""

import sys
import platform
import locale
from behave.textutil import select_best_encoding

def explore_platform_encoding():
    python_version = platform.python_version()
    print("python %s (platform: %s, %s, %s)" % (python_version, sys.platform,
                                            platform.python_implementation(),
                                            platform.platform()))
    print("sys.getfilesystemencoding():   %s" % sys.getfilesystemencoding())
    print("locale.getpreferredencoding(): %s" % locale.getpreferredencoding())
    print("behave.textutil.select_best_encoding(): %s" % select_best_encoding())
    return 0

if __name__ == "__main__":
    sys.exit(explore_platform_encoding())
