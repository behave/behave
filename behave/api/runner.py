# -*- coding: UTF-8 -*-
"""
Specifies the common interface for runner(s)/runner-plugin(s).

.. seealso::

    * https://pymotw.com/3/abc/index.html

"""

from __future__ import absolute_import
from abc import ABCMeta, abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class ITestRunner(object):
    """Interface that a test runner-class should provide:

    * Constructor: with config parameter object (at least) and some kw-args.
    * run() method without any args.
    """

    @abstractmethod
    def __init__(self, config, **kwargs):
        self.config = config

    @abstractmethod
    def run(self):
        """Run the selected features.

        :return: True, if test-run failed. False, on success.
        :rtype: bool
        """
        return False
