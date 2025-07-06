# -*- coding: UTF-8 -*-
# pylint: disable=useless-object-inheritance,super-with-arguments
# pylint: disable=consider-using-f-string
"""
This module provides an external visitor (using: Visitor design pattern)
to visit a model element and its items (by traversing the model tree).
"""

from __future__ import division, absolute_import, print_function
from behave._types import require_type
from behave.model import Feature, Rule, ScenarioOutline, Scenario, Step


class IModelVisitor(object):
    """Interface that must be implemented by a ``ModelVisitor`` class.
    Each ``ModelVisitor`` can override and implement a subset or
    all visitor methods.

    NOTES:

    * This class provides a ``NULL`` implementation (NULL design pattern)
      for all methods of the visitor-item API.
    """

    # -- VISITOR ITEM API: Concrete methods per model element type.
    def on_feature(self, feature):
        require_type(feature, Feature)

    def on_rule(self, rule):
        require_type(rule, Rule)

    def on_scenario_outline(self, scenario_outline):
        require_type(scenario_outline, ScenarioOutline)

    def on_scenario(self, scenario):
        require_type(scenario, Scenario)

    def on_step(self, step):
        require_type(step, Step)


class ModelVisitor(IModelVisitor):
    """Provides an abstract, external visitor of :mod:`behave.model` elements.

    RESPONSIBILITIES:

    * Provides support for visiting all model elements, like: Feature, ...
    * Walk the model tree structure to visit the contained model elements
    * function-like: Supports call API.

    NOTES:

    * Concrete visitor class(es) implement the interface :class:`IModelVisitor` .
    * Concrete visitor class(es) are either:

        * delegation-based  (implements: :class:`IModelVisitor`) or
        * inheritance-based (derives from: THIS-CLASS = :class:`ModelVisitor`)

    LOW-LEVEL DETAIL:

    * A visitor may abort the visitation sequence by returning ``False``.
    """

    def __init__(self, visitor=None):
        super(ModelVisitor, self).__init__()
        self.visitor = visitor or self
        require_type(self.visitor, IModelVisitor)

    @staticmethod
    def should_continue_visit(return_value):
        """
        A visit function can use:

        * NO_RETURN_VALUE (implicitly: None) -- MEANS: CONTINUE_VISIT
        * ``return_value=True``  -- MEANS: CONTINUE_VISIT
        * ``return_value=False`` -- MEANS: CANCEL_VISIT
        * ``return_value`` that converts into bool (with meanings described above)
        """
        return (return_value is None) or bool(return_value)

    # -- FUNCTION-LIKE CALL ADAPTER:
    def __call__(self, item):
        if isinstance(item, (list, tuple)):
            container = item
            return self.visit_many(container)
        # -- OTHERWISE:
        return self.visit(item)

    # -- VISIT AND WALK MODEL-ITEM TREE:
    def visit(self, item):
        """
        Visit a model element item.
        Determines which visit-method should be used and calls it.
        """
        # -- pylint: disable=no-else-return
        if isinstance(item, Feature):
            return self.visit_feature(item)
        elif isinstance(item, Rule):
            return self.visit_rule(item)
        elif isinstance(item, ScenarioOutline):
            return self.visit_scenario_outline(item)
        elif isinstance(item, Scenario):
            return self.visit_scenario(item)
        elif isinstance(item, Step):
            return self.visit_step(item)

        # -- OTHERWISE:
        raise TypeError("%r (not-supported)" % item)

    def visit_many(self, iterable, visit_func=None):
        visit_func = visit_func or self.visit
        for item in iterable:
            visit_result = visit_func(item)
            if not self.should_continue_visit(visit_result):
                return visit_result
        # -- VISITATION-COMPLETED:
        return True

    def visit_items_of(self, container, visit_func=None):
        return self.visit_many(iter(container), visit_func=visit_func)

    # -- VISITOR TREE WALK API:
    def visit_feature(self, feature):
        require_type(feature, Feature)
        visit_result = self.visitor.on_feature(feature)
        if self.should_continue_visit(visit_result):
            return self.visit_items_of(feature)
        # -- VISIT-CANCELLED:
        return visit_result

    def visit_rule(self, rule):
        require_type(rule, Rule)
        visit_result = self.visitor.on_rule(rule)
        if self.should_continue_visit(visit_result):
            return self.visit_items_of(rule)
        return visit_result

    def visit_scenario_outline(self, scenario_outline):
        require_type(scenario_outline, ScenarioOutline)
        visit_result = self.visitor.on_scenario_outline(scenario_outline)
        if self.should_continue_visit(visit_result):
            return self.visit_many(scenario_outline.scenarios,
                                   visit_func=self.visit_scenario)
        return visit_result

    def visit_scenario(self, scenario):
        require_type(scenario, Scenario)
        visit_result = self.visitor.on_scenario(scenario)
        if self.should_continue_visit(visit_result):
            return self.visit_items_of(scenario, visit_func=self.visit_step)
        return visit_result

    def visit_step(self, step):
        require_type(step, Step)
        return self.visitor.on_step(step)
