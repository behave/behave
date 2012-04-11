# -*- coding: utf-8 -*-
"""
Test utility functions for temporary files.
"""

from contextlib import contextmanager
from tempfile import NamedTemporaryFile
import os.path
from sys import version_info as python_version

@contextmanager
def named_temporary_file(delete_on_close=False, encoding="UTF-8"):
    """
    Context manager for creating, using and destroying a named temporary file.
    File is destroyed when context is exited.

    EXAMPLE:
        with named_temporary_file() as f:
            f.write("Hello")
            f.close()
            ...
        # -- POSTCONDITION: temporary file is destroyed HERE.
    """
    file_object = None
    if python_version[0] >= 3:
        # -- Python 3.x with encoding:
        # pylint: disable=E1123
        #   E1123   Passing unexpected keyword argument ... in function call
        #   => in Python 2.x
        file_object = NamedTemporaryFile(mode='w',
                                delete=delete_on_close, encoding=encoding)
    else:
        file_object = NamedTemporaryFile(mode='w', delete=delete_on_close)
    yield file_object
    file_object.close()
    if os.path.exists(file_object.name):
        os.remove(file_object.name)
