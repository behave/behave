# -*- coding: utf-8 -*-

class Reporter(object):
    """
    Base class for all reporters.
    A reporter provides an extension point (variant point) for the runner logic.
    A reporter is called after a model element is processed
    (and its result status is known).
    Otherwise, a reporter is similar to a formatter, but it has a simpler API.

    Processing Logic (simplified)::

        config.reporters = ...  #< Configuration (and provision).
        runner.run():
            for feature in runner.features:
                feature.run()     # And feature scenarios, too.
                for reporter in config.reporters:
                    reporter.feature(feature)
            # -- FINALLY:
            for reporter in config.reporters:
                reporter.end()

    An existing formatter can be reused as reporter by using
    :class:`behave.report.formatter_reporter.FormatterAsReporter`.
    """
    def __init__(self, config):
        self.config = config

    def feature(self, feature):
        """
        Called after a feature was processed.

        :param feature:  Feature object (as :class:`behave.model.Feature`)
        """
        assert feature.status in ("skipped", "passed", "failed")
        raise NotImplementedError

    def end(self):
        """
        Called after all model elements are processed (optional-hook).
        """
        pass
