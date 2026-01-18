"""
Specifies the common interface for runner(s)/runner-plugin(s).

.. seealso::

    * https://pymotw.com/3/abc/index.html

"""

from abc import ABCMeta, abstractmethod


class ITestRunner(metaclass=ABCMeta):
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

    @property
    @abstractmethod
    def undefined_steps(self):
        """Provides list of undefined steps that were found during the test-run.

        :return: List of unmatched steps (as string) in feature-files.
        """
        raise NotImplementedError()
        # return NotImplemented
