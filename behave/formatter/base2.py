from __future__ import absolute_import, print_function

from behave.formatter.api import IFormatter2
from behave.formatter.base import Formatter

# -----------------------------------------------------------------------------
# FORMATTER BASE CLASSES:
# -----------------------------------------------------------------------------
class BaseFormatter2(Formatter, IFormatter2):
    """
    Base formatter class for using the :class:`IFormatter2` interface.

    RESPONSIBILITIES:

    * Implements the :class:`behave.formatter.base.IFormatter` interface.
    * Implements the :class:`behave.formatter.core.IFormatter2` interface.
    * Provides generic core functionality of a formatter.
    * Maps the :class:`IFormatter` interface to :class:`IFormatter2` interface.
    * Contains some sanity checks if formatter calls are missing.
    """
    def __init__(self, stream_opener, config, to_formatter=None):
        super(BaseFormatter2, self).__init__(stream_opener, config)
        self.formatter = to_formatter or self
        self.current_testrun_started = None
        self.current_file = None
        self.current_feature = None
        self.current_rule = None
        self.current_scenario = None
        self.current_step = None

    # -- INTERFACE FOR: Formatter
    def uri(self, uri):
        self._ensure_testrun_started()
        self._finish_current_file()
        self.current_file = uri
        self.formatter.on_file_start(uri)

    def feature(self, this_feature):
        self._ensure_testrun_started()
        self._finish_current_feature()
        self._ensure_file_started(this_feature.location.filename)
        self.current_feature = this_feature
        self.formatter.on_feature_start(self.current_feature)

    def background(self, this_background):
        pass    # -- IGNORE.

    def rule(self, this_rule):
        self._finish_current_rule_or_scenario()
        self.current_rule = this_rule
        self.formatter.on_rule_start(self.current_rule)

    def scenario(self, this_scenario):
        self._finish_current_scenario()
        self.current_scenario = this_scenario
        self.formatter.on_scenario_start(self.current_scenario)

    def step(self, this_step):
        self.formatter.on_step_start(this_step)

    def result(self, this_step):
        self.formatter.on_step_end(this_step)
        if self.current_step is this_step:
            self.current_step = None

    def eof(self):
        self._finish_current_file()

    def close(self):
        self._finish_current_testrun()
        self.close_stream()

    # -- SPECIFIC:
    def _ensure_testrun_started(self):
        if self.current_testrun_started:
            return

        self.current_testrun_started = True
        self.formatter.on_testrun_start()

    def _ensure_file_started(self, uri):
        self._ensure_testrun_started()
        if self.current_file and uri == self.current_file:
            return

        self.current_file = uri
        self.formatter.on_file_start(uri)

    def _finish_current_step(self):
        if self.current_step is None:
            return

        self.formatter.on_step_end(self.current_step)
        self.current_step = None

    def _finish_current_scenario(self):
        if self.current_scenario is None:
            return

        self._finish_current_step()
        self.formatter.on_scenario_end(self.current_scenario)
        self.current_scenario = None

    def _finish_current_rule_or_scenario(self):
        if self.current_rule is None:
            self._finish_current_scenario()
            return

        self._finish_current_scenario()
        self.formatter.on_rule_end(self.current_rule)
        self.current_rule = None

    def _finish_current_rule(self):
        self._finish_current_rule_or_scenario()

    def _finish_current_feature(self):
        if self.current_feature is None:
            return

        self._finish_current_rule_or_scenario()
        self.formatter.on_feature_end(self.current_feature)
        self.current_feature = None

    def _finish_current_file(self):
        if self.current_file is None:
            return

        self._finish_current_feature()
        self.formatter.on_file_end(self.current_file)
        self.current_file = None

    def _finish_current_testrun(self):
        if not self.current_testrun_started:
            return

        self._finish_current_file()
        self.formatter.on_testrun_end()
        self.current_testrun_started = False

    def _finish_any_elements(self):
        self._finish_current_step()
        self._finish_current_scenario()
        self._finish_current_rule()
        self._finish_current_feature()
        self._finish_current_file()
        self._finish_current_testrun()
