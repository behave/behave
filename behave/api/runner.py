# -*- coding: UTF-8 -*-
"""
Specifies the common interface for runner(s)/runner-plugin(s).

.. seealso::

    * https://pymotw.com/3/abc/index.html

"""

from __future__ import absolute_import
from abc import ABCMeta, abstractmethod
from sys import version_info as _version_info
from six import add_metaclass


_PYTHON_VERSION = _version_info[:2]


@add_metaclass(ABCMeta)
class ITestRunner(object):
    """Interface that a test runner-class should provide:

    * Constructor: with config parameter object (at least) and some kw-args.
    * run() method without any args.
    """

    @abstractmethod
    def __init__(self, config, **kwargs):
        self.config = config
        # MAYBE: self.undefined_steps = []

    @abstractmethod
    def run(self):
        """Run the selected features.

        :return: True, if test-run failed. False, on success.
        :rtype: bool
        """
        return False

    # if _PYTHON_VERSION < (3, 3):
    #     # -- HINT: @abstractproperty, deprecated since Python 3.3
    #     from abc import abstractproperty
    #     @abstractproperty
    #     def undefined_steps(self):
    #         raise NotImplementedError()
    # else:
    @property
    @abstractmethod
    def undefined_steps(self):
        """Provides list of undefined steps that were found during the test-run.

        :return: List of unmatched steps (as string) in feature-files.
        """
        raise NotImplementedError()
        # return NotImplemented
