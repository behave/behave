"""
Defines interface(s) for formatter classes.
"""


# -----------------------------------------------------------------------------
# FORMATTER INTERFACE:
# -----------------------------------------------------------------------------
class IFormatter(object):
    """
    Provides the main interface for formatter classes.

    A formatter is an extension point (variation point) for the runner logic.
    A formatter is called while processing model elements.

    Processing Logic (simplified, without ScenarioOutline and skip logic):

    .. code-block:: python

        # -- HINT: Rule processing is missing.
        for feature in runner.features:
            formatter = make_formatters(...)
            formatter.uri(feature.filename)
            formatter.feature(feature)
            for scenario in feature.walk_scenarios():
                formatter.scenario(scenario)
                for step in scenario.all_steps:
                    formatter.step(step)
                    step_match = step_registry.find_match(step)
                    formatter.match(step_match)
                    if step_match:
                        step_match.run()
                    else:
                        step.status = Status.undefined
                    formatter.result(step.status)
            formatter.eof() # -- FEATURE-END
        formatter.close()

    .. note::

        Processing of steps works slightly differently from description here.
    """
    name = None
    description = None

    def uri(self, uri):
        """Called before processing a file (normally a feature file).

        :param uri:  URI or filename (as string).
        """
        pass

    def feature(self, feature):
        """Called before a feature is executed.

        :param feature:  Feature object (as :class:`behave.model.Feature`)
        """
        pass

    def rule(self, rule):
        """Called before a rule is executed.

        :param rule:  Rule object (as :class:`behave.model.Rule`)
        """
        pass

    # @deprecated
    def background(self, background):
        """
        Called when a Feature/Rule Background is provided.
        Called after :method:`feature()` is called.
        Called before processing any scenarios or scenario outlines.

        :param background:  Background object (as :class:`behave.model.Background`)
        """
        pass

    def scenario(self, scenario):
        """Called before a scenario is executed (or ScenarioOutline scenarios).

        :param scenario:  Scenario object (as :class:`behave.model.Scenario`)
        """
        pass

    def step(self, step):
        """Called before a step is executed (and matched).
        NOTE: Normally called before scenario is executed for all its steps.

        :param step: Step object (as :class:`behave.model.Step`)
        """
        pass

    def match(self, match):
        """Called when a step was matched against its step implementation.

        :param match:  Registered step (as Match), undefined step (as NoMatch).
        """
        pass

    def result(self, step):
        """Called after processing a step (when the step result is known).

        :param step:  Step object with result (after being executed/skipped).
        """
        pass

    def eof(self):
        """Called after processing a feature (or a feature file)."""
        pass

    def close(self):
        """
        Called before the formatter is no longer used.
        Should close its stream.
        """
        raise NotImplementedError()


# -----------------------------------------------------------------------------
# FORMATTER INTERFACE (VARIANT 2 -- Needs interface adapter)
# -----------------------------------------------------------------------------
class IFormatter2:
    """
    Provides a simpler interface for formatter classes.
    """
    def on_testrun_start(self):
        pass

    def on_testrun_end(self):
        pass

    def on_file_start(self, uri):
        pass

    def on_file_end(self, uri):
        pass


    def on_feature_start(self, this_feature):
        pass

    def on_feature_end(self, this_feature):
        pass

    def on_rule_start(self, this_rule):
        pass

    def on_rule_end(self, this_rule):
        pass

    def on_scenario_start(self, this_scenario):
        pass

    def on_scenario_end(self, this_scenario):
        pass

    def on_step_start(self, this_step):
        pass

    def on_step_end(self, this_step):
        pass
