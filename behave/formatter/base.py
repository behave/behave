# -*- coding: utf-8 -*-


class Formatter(object):
    """
    Base class for all formatter classes.
    A formatter is an extension point (variation point) for the runner logic.
    A formatter is called while processing model elements.

    Processing Logic (simplified, without ScenarioOutline and skip logic)::

        for feature in runner.features:
            formatter = get_formatter(...)
            formatter.uri(feature.filename)
            formatter.feature(feature)
            for scenario in feature.scenarios:
                formatter.scenario(scenario)
                for step in scenario.all_steps:
                    formatter.step(step)
                    step_match = step_registry.find_match(step)
                    formatter.match(step_match)
                    if step_match:
                        step_match.run()
                    else:
                        step.status = "undefined"
                    formatter.result(step.status)
            # -- FEATURE-END
            formatter.close()
    """
    name = None
    description = None

    def __init__(self, stream, config):
        self.stream = stream
        self.config = config

    def uri(self, uri):
        """
        Called before processing a file (normally a feature file).

        :param uri:  URI or filename (as string).
        """
        pass

    def feature(self, feature):
        """
        Called before a feature is executed.

        :param feature:  Feature object (as :class:`behave.model.Feature`)
        """
        pass

    def background(self, background):
        """
        Called when a (Feature) Background is provided.
        Called after :method:`feature()` is called.
        Called before processing any scenarios or scenario outlines.

        :param background:  Background object (as :class:`behave.model.Background`)
        """
        pass

    def scenario(self, scenario):
        """
        Called before a scenario is executed (or an example of ScenarioOutline).

        :param scenario:  Scenario object (as :class:`behave.model.Scenario`)
        """
        pass

    def scenario_outline(self, outline):
        pass

    def examples(self, examples):
        pass

    def step(self, step):
        """
        Called before a step is executed (and matched).

        :param step: Step object (as :class:`behave.model.Step`)
        """

    def match(self, match):
        """
        Called when a step was matched against its step implementation.

        :param match:  Registered step (as Match), undefined step (as NoMatch).
        """
        pass

    def result(self, step_result):
        """
        Called after processing a step (when the step result is known).

        :param step_result:  Step result (as string-enum).
        """
        pass

    def eof(self):
        """
        Called after processing a feature (or a feature file).
        """
        pass

    def close(self):
        """
        Called before the formatter is no longer used (stream/io compatibility).
        """
        pass
