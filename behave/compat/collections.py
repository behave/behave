# -*- coding: utf-8 -*-
"""
Compatibility of :module:`collections` between different Python versions.
"""

from __future__ import absolute_import
import warnings
# pylint: disable=unused-import
try:
    # -- SINCE: Python2.7
    from collections import OrderedDict
except ImportError:     # pragma: no cover
    try:
        # -- BACK-PORTED FOR: Python 2.4 .. 2.6
        from ordereddict import OrderedDict
    except ImportError:
        message = "collections.OrderedDict is missing: Install 'ordereddict'."
        warnings.warn(message)
        # -- BACKWARD-COMPATIBLE: Better than nothing (for behave use case).
        OrderedDict = dict

try:
    from collections import UserDict
except ImportError:      # pragma: no cover
    class UserDict(object):
        """Emulate collections.UserDict class in python3."""
        def __init__(self, data=None):
            if data is None:
                data = {}
            self.data = data

        def __len__(self):
            return len(self.data)

        def __iter__(self):
            return len(self.data)

        def keys(self):
            return self.data.keys()

        def values(self):
            return self.data.values()

        def items(self):
            return self.data.items()
