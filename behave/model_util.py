# -*- coding: utf-8 -*-
"""
This module provides a number of utility classes and functions that operate
on model elements.
"""

from behave import model

def select_step_with_status(status, steps):
    """
    Helper function to find the first step with the given step.status.

    EXAMPLE: Search for a failing step in a scenario (all steps).
        >>> scenario = ...
        >>> failed_step = select_step_with_status("failed", scenario)
        >>> failed_step = select_step_with_status("failed", scenario.all_steps)
        >>> assert failed_step.status == "failed"

    EXAMPLE: Search only scenario steps, skip background steps.
        >>> failed_step = select_step_with_status("failed", scenario.steps)

    :param status:  Step status to search for (as string).
    :param steps:   List of steps to search in (or scenario).
    :returns: Step object, if found.
    :returns: None, otherwise.
    """
    for step in steps:
        assert isinstance(step, model.Step), "TYPE-MISMATCH: "+\
                        "step.class={0}".format(step.__class__.__name__)
        if step.status == status:
            return step
    # -- OTHERWISE: No step with the given status found.
    # KeyError("Step with status={0} not found".format(status))
    return None

def select_steps_with_status(status, steps):
    """
    Helper function to find all steps that have the given step.status.

    :param status:  Step status to search for (as string).
    :param steps:   List of steps to search in.
    :returns: List of step with this status.
    :returns: Empty list, otherwise.
    """
    return [ step  for step in steps if step.status == status ]


class ModelDescriptor(object):
    """
    Utility class to describe model elements in readable text form.
    Primary purpose:
      * Beautify parsed model and model elements
      * Diagnostics: Dump model data as text
      * Reuse: Avoid reimplementing of parts in formatters, reporters, ...
    """
    ALIAS_PARAMS = {
        "show_multiline":   "show_text",
    }

    def __init__(self, **kwargs):
        self.compact = False
        self.show_text  = True
        self.show_table = True
        self.show_status = False
        self.show_timings = False
        for name, value in kwargs.items():
            realname = self.ALIAS_PARAMS.get(name, None)
            if realname:
                name = realname
            setattr(self, name, value)
            if name == "indent":
                self.prefix = u" " * value

        if self.compact:
            self.show_text  = False
            self.show_table = False

    def describe(self, model_element, **kwargs):
        """
        Main method that automatically detects the model element type
        and delegates to the specific method for this model element.
        """
        if isinstance(model_element, model.ScenarioOutline):
            return self.describe_scenario_outline(model_element, **kwargs)
        elif isinstance(model_element, model.Scenario):
            return self.describe_scenario(model_element, **kwargs)
        raise AttributeError("{0} is nor supported yet".format(
                model_element.__class__.__name__))

    def describe_feature(self, feature, **kwargs):
        assert isinstance(feature, model.Feature)
        raise NotImplementedError

        # description
        # Background
        # Scenario or ScenarioOutline

    def describe_background(self, background, **kwargs):
        assert isinstance(background, model.Background)
        show_status = kwargs.pop("show_status", self.show_status)
        prefix = self.prefix
        text = u'{0}{1}: {2}\n'.format(prefix, background.keyword, background.name)
        prefix += u'  '
        for step in background.steps:
            text += self.describe_step(step, prefix=prefix,
                                    show_status=show_status)
        return text

    def describe_scenario_outline(self, scenario_outline, **kwargs):
        assert isinstance(scenario_outline, model.ScenarioOutline)
        text = u''
        for scenario in scenario_outline:
            text += self.describe_scenario(scenario, **kwargs)
            text += u'\n'
        return text

    def describe_scenario(self, scenario, show_status=None):
        """
        Provide a textual description of the scenario.

        :param indent:  Number of chars to indent.
        :param show_status:  If true, indicates if step.status should provided.
        :param compact:      if true, does not show step.text and step.table.
        :return:  Textual description of this scenario.
        """
        assert isinstance(scenario, model.Scenario)
        # -- OPEN ISSUE: Does this work w/ ScenarioOutline, too ?!?
        if show_status is None:
            show_status = self.show_status
        prefix = self.prefix
        text = u'{0}{1}: {2}\n'.format(prefix, scenario.keyword, scenario.name)
        prefix += u'  '
        for step in scenario.all_steps:
            text += self.describe_step(step, prefix=prefix,
                            show_status=show_status)
        return text

    def describe_step(self, step, **kwargs):
        prefix  = kwargs.get("prefix", self.prefix)
        show_status = kwargs.get("show_status", self.show_status)

        text = u'%s%6s %s' % (prefix, step.keyword, step.name)
        if show_status:
            text += u'  ... {0}'.format(step.status)
        text += u'\n'
        if step.text is not None and self.show_text:
            # -- CASE: Show multi-line text.
            text += u'{0}     """\n'.format(prefix)
            for line in step.text.splitlines():
                text += u'{0}     {1}\n'.format(prefix, line)
            text += u'{0}     """\n'.format(prefix)
        elif step.table and self.show_table:
            # -- CASE: Show table.
            text += self.describe_table(step.table)
        return text

    def describe_table(self, table, **kwargs):
        # XXX-JE-TODO
        # raise NotImplementedError
        pass
        return

    def describe_examples(self, examples, **kwargs):
        # XXX-JE-TODO
        return self.describe_table(examples)


def describe(model_element, **kwargs):
    """
    Convenience function to get a textual description of a model element.
    :param model_element:   Model element that should be described.
    :returns: Textual description (as string)
    """
    model_descriptor = ModelDescriptor(**kwargs)
    return model_descriptor.describe(model_element)