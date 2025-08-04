# -*- coding: UTF-8 -*-
# pylint: disable=useless-object-inheritance,
# pylint: disable=super-with-arguments
# pylint: disable=consider-using-f-string
# pylint: disable=redundant-u-string-prefix
"""
This module provides helper class to simplify building many model elements.
"""

from __future__ import absolute_import, print_function
import functools
from behave.model import Scenario, Step, Feature, Rule
from behave.model_type import Status
from behave._types import Unknown


# -----------------------------------------------------------------------------
# BUILDER VIEW CLASSES:
# -----------------------------------------------------------------------------
class BuilderView(object):
    @staticmethod
    def select_builder_attribute(builder, name, default=None):
        if name.startswith("_"):
            # -- SHORTCUT: Only support lookup for public attribs/funcs.
            return None

        while builder is not None:
            print("DIAG select_builder_attribute: name=%s, builder=%r::id=%s" % \
                  (name, builder, id(builder)))
            builder_attribute = getattr(builder, name, Unknown)
            if builder_attribute is not Unknown:
                print("DIAG select_builder_attribute: name=%s = %s" % \
                      (name, builder_attribute))
                return builder_attribute
            # -- OTHERWISE: Use builder=builder.parent
            builder = getattr(builder, "parent", None)
        return default


class BuilderContext(BuilderView):
    BUILDER_FUNCTION_PREFIXES = ["with_", "and_"]

    @classmethod
    def is_builder_function(cls, func_name):
        if not func_name.startswith("_"):
            for prefix in cls.BUILDER_FUNCTION_PREFIXES:
                if func_name.startswith(prefix):
                    return True
        # -- NOT-FOUND:
        return False

    @staticmethod
    def make_function_with_ctx(func, ctx):
        return functools.partial(func, ctx)

    def __init__(self, builder, current_items):
        self.builder = builder
        self._current_items = current_items or []

    @property
    def current_items(self):
        return self._current_items

    def __iter__(self):
        return iter(self.current_items)

    def __len__(self):
        return len(self.current_items)

    def _select_builder_attribute(self, name, default=None):
        return self.select_builder_attribute(self.builder, name, default)

    # -- PROXY-FOR: Builder
    def __getattr__(self, name):
        builder_attribute = self._select_builder_attribute(name)
        if builder_attribute is not None:
            if callable(builder_attribute) and self.is_builder_function(name):
                func = builder_attribute
                return self.make_function_with_ctx(func, self)
            return builder_attribute
        # MAYBE: item access
        # -- OTHERWISE:
        raise AttributeError
        # return super(BuilderItemView, self).__getattribute__(name)


class  BuilderOperationsMixin(object):
    @staticmethod
    def with_names(ctx, names, default_name=None):
        assert isinstance(ctx, BuilderContext)
        names_size = len(names)
        for index, current in enumerate(ctx):
            name = default_name
            if index < names_size:
                name = names[index]
            if name:
                current.name = name
        return ctx

    @staticmethod
    def with_status(ctx, status):
        assert isinstance(ctx, BuilderContext)
        for current in ctx:
            current.set_status(status)
        return ctx

    @classmethod
    def with_outcome(cls, ctx, outcome):
        return cls.with_status(ctx, outcome)

    @classmethod
    def with_outcomes(cls, ctx, outcomes, default=Status.untested):
        assert isinstance(ctx, BuilderContext)
        outcomes_size = len(outcomes)
        for index, current in enumerate(ctx):
            status = default
            if index < outcomes_size:
                status = outcomes[index]
            current.set_status(status)
        return ctx

    # def with_scenario(self, ctx, scenario=None, **scenario_kwargs):
    #     assert isinstance(ctx, BuilderContext)
    #     for current in ctx:
    #         if isinstance(current, (Feature, Rule)):
    #             self.add_scenario(current, scenario=scenario, **scenario_kwargs)
    #     return ctx

    # def with_step(self, ctx, step=None, **step_kwargs):
    #     assert isinstance(ctx, BuilderContext)
    #     for current in ctx:
    #         if not isinstance(current, Scenario):
    #             self.add_step(current, step=step, **step_kwargs)
    #     return ctx

# class BuilderItemView(BuilderView):
#     def __init__(self, builder, item):
#         self.builder = builder
#         self._model_item = item
#
#     def current_sequence(self):
#         return [self._model_item]
#
#     @property
#     def model_item(self):
#         return self._model_item
#
#     def with_name(self, name):
#         self.model_item.name = name
#         return self
#
#     def with_status(self, status):
#         self.model_item.set_status(status)
#         return self
#
#     def with_outcome(self, outcome):
#         return self.with_status(outcome)
#
#     def _select_builder_attribute(self, name, default=None):
#         return self.select_builder_attribute(self.builder, name, default)
#
#     # -- PROXY-FOR: Builder
#     def __getattr__(self, name):
#         builder_attribute = self._select_builder_attribute(name)
#         if builder_attribute is not None:
#             return builder_attribute
#         # MAYBE: item access
#         # -- OTHERWISE:
#         raise AttributeError
#         # return super(BuilderItemView, self).__getattribute__(name)
#
#
# class BuilderSequenceView(BuilderView):
#     def __init__(self, builder, data, offset=0):
#         assert offset >= 0, "REQUIRE NON-NEGATIVE: %s" % offset
#         self.builder = builder
#         self.data = data
#         self.offset = offset
#
#     @property
#     def sequence(self):
#         return self.data[self.offset:]
#
#     def current_sequence(self):
#         return self.sequence
#
#     def with_names(self, names, default_name=None):
#         names_size = len(names)
#         for index, item in enumerate(self.current_sequence()):
#             name = default_name
#             if index < names_size:
#                 name = names[index]
#             if name:
#                 item.name = name
#         return self
#
#     def with_status(self, status):
#         for item in self.current_sequence():
#             item.set_status(status)
#         return self
#
#     def with_outcome(self, outcome):
#         return self.with_status(outcome)
#
#     def with_outcomes(self, outcomes, default=Status.passed):
#         outcomes_size = len(outcomes)
#         for index, item in enumerate(self.current_sequence):
#             status = default
#             if index < outcomes_size:
#                 status = outcomes[index]
#             item.set_status(status)
#         return self
#
#     # -- API FOR: Builder
#     def _select_builder_attribute(self, name, default=None):
#         return self.select_builder_attribute(self.builder, name, default)
#
#     def _make_call_proxy(self, func):
#         this_class = self.__class__
#         def _caller(*args, **kwargs):
#             result = func(*args, **kwargs)
#             if isinstance(result, BuilderSequenceView):
#                 return this_class(result.builder, data=self.sequence)
#             elif isinstance(result, BuilderItemView):
#                 return this_class(result.builder, data=self.sequence)
#         return _caller
#
#     def __getattr__(self, name):
#         builder_attribute = self._select_builder_attribute(name)
#         if builder_attribute is not None:
#             if callable(builder_attribute):
#                 return self._make_call_proxy(builder_attribute)
#             return builder_attribute
#         # -- OTHERWISE:
#         # return super(BuilderSequenceView, self).__getattribute__(name)
#         raise AttributeError
#
#     # -- PROXY-API FOR: Sequence
#     def append(self, item):
#         self.data.append(item)
#
#     def extend(self, items):
#         self.data.extend(items)
#
#     def __len__(self):
#         return len(self.data) - self.offset
#
#     def __iter__(self):
#         return iter(self.sequence)
#
#     def __getitem__(self, pos):
#         return self.sequence[pos]
#
#
# -----------------------------------------------------------------------------
# BUILDER MIXIN CLASSES:
# -----------------------------------------------------------------------------
class FilenameBuilderMixin(object):
    FILENAME_SCHEMA = "features/f_{0:03d}.feature"
    COUNTER = 0

    @classmethod
    def make_filename(cls):
        cls.COUNTER += 1
        filename = cls.FILENAME_SCHEMA.format(cls.COUNTER)
        return filename


class FeatureBuilderMixin(FilenameBuilderMixin):
    FEATURE_DEFAULT_PARAMS = {
        "keyword": u"Feature",
        "name": u"",
        "line": 0,
    }

    def make_feature(self, **kwargs):
        filename = kwargs.pop("filename", None)
        if filename is None:
            filename = self.make_filename()
        feature_kwargs = self.FEATURE_DEFAULT_PARAMS.copy()
        feature_kwargs.update(kwargs)
        return Feature(filename=filename, **feature_kwargs)


class ManyFeaturesBuilderMixin(FeatureBuilderMixin):

    @property
    def features(self):
        raise NotImplementedError()

    def add_feature(self, **feature_kwargs):
        feature = self.make_feature(**feature_kwargs)
        self.features.append(feature)
        return BuilderContext(self, [feature])

    def add_many_features(self, count, **feature_kwargs):
        offset = len(self.features)
        for index in range(count):
            self.add_feature(**feature_kwargs)
        return BuilderContext(self, self.features[offset:])
        # return BuilderSequenceView(builder=self, data=self.features, offset=offset)


class RuleBuilderMixin(object):

    def make_rule(self, **kwargs):
        filename = kwargs.pop("filename", None)
        if filename is None:
            filename = getattr(self, "filename", None)
            if not filename:
                filename = FilenameBuilderMixin.make_filename()
        return Rule(filename=filename, **kwargs)


class ManyRulesBuilderMixin(RuleBuilderMixin):
    @property
    def feature(self):
        raise NotImplementedError()

    # def current_sequence(self):
    #     raise NotImplementedError()

    # -- BUILDER API FOR: Rules
    def add_rule(self, rule=None, current=None, **rule_kwargs):
        current_feature = current or self.feature
        assert isinstance(current, Feature)
        if rule is None:
            rule = self.make_rule(**rule_kwargs)
        current_feature.add_rule(rule)
        return BuilderContext(self, [rule])
        # return BuilderItemView(builder=self, item=rule)

    def add_many_rules(self, count, current=None, **rule_kwargs):
        current_feature = current or self.feature
        offset = len(current_feature.rules)
        for index in range(count):
            self.add_rule(**rule_kwargs)
        return BuilderContext(self, current_feature.rules[offset:])
        # return BuilderSequenceView(builder=self, data=current_feature.rules, offset=offset)

    def with_rule(self, ctx, rule=None, **rule_kwargs):
        assert isinstance(ctx, BuilderContext)
        for current in ctx:
            if not isinstance(current, Feature):
                print("IGNORED: with_rule() on=%r (expected: Feature)" % current)
                continue

            self.add_rule(rule=rule, current=current, **rule_kwargs)
        return BuilderContext(self, ctx.current_items)
        # return BuilderSequenceView(builder=self, data=self.current_sequence())

    def with_many_rules(self, ctx, count, **rule_kwargs):
        assert isinstance(ctx, BuilderContext)
        for current in ctx:
            if not isinstance(current, Feature):
                print("IGNORED: with_many_rule(%d) on=%r (expected: Feature)" % (count, current))
                continue
            self.add_many_rules(count, current=current, **rule_kwargs)
        return BuilderContext(self, ctx.current_items)
        # return BuilderSequenceView(builder=self, data=self.current_sequence())


class ScenarioBuilderMixin(object):
    SCENARIO_DEFAULT_PARAMS = {
        "keyword": u"Scenario",
        "name": u"",
        "line": 0,
    }

    def make_scenario(self, dry_run=False, **kwargs):
        filename = getattr(self, "filename", None)
        if filename is None:
            filename = FilenameBuilderMixin.make_filename()

        tail_scenario_last_line = 10
        scenarios = getattr(self, "scenarios", None)
        if scenarios:
            tail_scenario = scenarios[-1]
            tail_scenario_last_line = tail_scenario.line
            if tail_scenario.steps:
                tail_scenario_last_line = tail_scenario.steps[-1].line

        scenario_kwargs = self.SCENARIO_DEFAULT_PARAMS.copy()
        scenario_kwargs.update({
            "filename": filename,
            "line": tail_scenario_last_line + 10,
        })
        scenario_kwargs.update(kwargs)
        scenario = Scenario(**scenario_kwargs)
        scenario.was_dry_run = dry_run
        return scenario

class ManyScenariosBuilderMixin(ScenarioBuilderMixin):

    @property
    def scenario_container(self):
        raise NotImplementedError()

    def add_scenario(self, scenario=None, current=None, **scenario_kwargs):
        scenario_container = current or self.scenario_container
        if scenario is None:
            scenario = self.make_scenario(**scenario_kwargs)
        scenario_container.add_scenario(scenario)
        return BuilderContext(self, [scenario])
        # return BuilderItemView(builder=self, item=scenario)

    def add_many_scenarios(self, count, current=None, **scenario_kwargs):
        scenario_container = current or self.scenario_container
        offset = len(scenario_container.scenarios)
        name = scenario_kwargs.pop("name", "")
        for index in range(count):
            scenario_name = u"{name}_{index}".format(name=name, index=index)
            scenario_kwargs["name"] = scenario_name.strip()
            self.add_scenario(current=scenario_container, **scenario_kwargs)
        return BuilderContext(self, scenario_container.scenarios[offset:])
        # return BuilderSequenceView(self, self.scenario_container.scenarios, offset)

    def with_scenario(self, ctx, scenario=None, **scenario_kwargs):
        assert isinstance(ctx, BuilderContext)
        for current in ctx:
            if not isinstance(current, (Feature, Rule)):
                print("SKIP with_scenario: current=%r (expected: Feature, Rule)" % current)
                continue
            self.add_scenario(scenario=scenario, current=current, **scenario_kwargs)
        return BuilderContext(self, ctx.current_items)
        # return BuilderSequenceView(builder=self, data=self.current_sequence())

    def with_many_scenarios(self, ctx, count, **scenario_kwargs):
        assert isinstance(ctx, BuilderContext)
        for current in ctx:
            if not isinstance(current, (Feature, Rule)):
                print("SKIP with_many_scenarios(%d): current=%r (expected: Feature, Rule)" % \
                      (count, current))
                continue
            self.add_many_scenarios(count, current=current, **scenario_kwargs)
        return BuilderContext(self, ctx.current_items)
        # return BuilderSequenceView(builder=self, data=self.current_sequence())


class ManyStepsBuilderMixin(object):
    DEFAULT_STEP = u"a step passes"
    DEFAULT_STEP_KEYWORD = u"Given"
    DEFAULT_STEP_TYPE = u"given"

    @property
    def steps(self):
        raise NotImplementedError()

    def make_step(self, **kwargs):
        filename = getattr(self, "filename", )
        if filename is None:
            filename = FilenameBuilderMixin.make_filename()

        last_step_line = 10
        if self.steps:
            last_step_line = self.steps[-1].line

        step_kwargs = {
            "filename": filename,
            "line": last_step_line + 1,
            "name": self.DEFAULT_STEP,
            "keyword": self.DEFAULT_STEP_KEYWORD,
            "step_type": self.DEFAULT_STEP_TYPE,
        }
        status = kwargs.pop("status", Status.untested)
        step_kwargs.update(kwargs)
        step = Step(**step_kwargs)
        step.set_status(status)
        return step

    def add_step(self, step=None, current=None, **step_kwargs):
        current_scenario = current or self.scenario
        assert isinstance(current_scenario, Scenario), "OOPS: %r" % current_scenario
        if step is None:
            step = self.make_step(**step_kwargs)
        current_scenario.steps.append(step)
        return BuilderContext(self, [step])
        # return BuilderItemView(builder=self, item=step)

    def add_many_steps(self, count, current=None, **step_kwargs):
        current_scenario = current or self.scenario
        assert isinstance(current_scenario, Scenario), "OOPS: %r" % current_scenario
        offset = len(current_scenario.steps)
        for index in range(count):
            self.add_step(current=current_scenario, **step_kwargs)
        return BuilderContext(self, current_scenario.steps[offset:])
        # return BuilderSequenceView(builder=self, data=current_scenario.steps, offset=offset)

    def with_step(self, ctx, step=None, **step_kwargs):
        assert isinstance(ctx, BuilderContext)
        for current in ctx:
            if not isinstance(current, Scenario):
                print("SKIP with_step: current=%r (expected: Scenario)" % current)
                continue
            self.add_step(step, current=current, **step_kwargs)
        return BuilderContext(self, ctx.current_items)
        # return BuilderSequenceView(builder=self, data=self.current_sequence())

    def with_many_steps(self, ctx, count, outcomes=None, **step_kwargs):
        assert isinstance(ctx, BuilderContext)
        for current in ctx:
            if not isinstance(current, Scenario):
                print("SKIP with_step: current=%r (expected: Scenario)" % current)
                continue
            ctx2 = self.add_many_steps(count, current=current, **step_kwargs)
            if outcomes:
                self.with_outcomes(ctx2, outcomes)
        return BuilderContext(self, ctx.current_items)
        # return BuilderSequenceView(builder=self, data=self.current_sequence())


# -----------------------------------------------------------------------------
# BUILDER CLASSES:
# -----------------------------------------------------------------------------
# DISABLED: class ScenarioBuilder(BuilderSequenceView, FilenameBuilderMixin,
class ScenarioBuilder(BuilderOperationsMixin, FilenameBuilderMixin,
                      ScenarioBuilderMixin, ManyStepsBuilderMixin):
    """Builds one scenario."""

    def __init__(self, scenario=None, dry_run=False, **scenario_kwargs):
        if scenario is None:
            scenario = self.make_scenario(**scenario_kwargs)
        # DISABLED: super(ScenarioBuilder, self).__init__(self, scenario.steps)
        super(ScenarioBuilder, self).__init__()
        scenario.was_dry_run = dry_run
        self.scenario = scenario

    @property
    def filename(self):
        return self.scenario.filename

    @property
    def steps(self):
        return self.scenario.steps


# DISABLED: class ManyScenariosBuilder(BuilderSequenceView, FeatureBuilderMixin,
class ManyScenariosBuilder(BuilderOperationsMixin,
                           FeatureBuilderMixin,
                           ManyScenariosBuilderMixin,
                           ManyStepsBuilderMixin):

    def __init__(self, feature_or_rule=None, **container_kwargs):
        scenario_container = feature_or_rule
        if feature_or_rule is None:
            self._feature = self.make_feature(**container_kwargs)
            scenario_container = self._feature
        elif isinstance(feature_or_rule, Feature):
            self._feature = feature_or_rule
        elif isinstance(feature_or_rule, Rule):
            self._rule = feature_or_rule
            self._feature = None
        else:
            raise TypeError("%r (expected: Feature, Rule)" % feature_or_rule)

        self._scenario_container = scenario_container
        super(ManyScenariosBuilder, self).__init__()
        # DISABLED: super(ManyScenariosBuilder, self).__init__(builder=self,
        # DISABLED:                                            data=self.scenarios)

    @property
    def scenario_container(self):
        return self._scenario_container

    @property
    def filename(self):
        return self.scenario_container.filename

    @property
    def scenarios(self):
        return self.scenario_container.scenarios

    @property
    def steps(self):
        if self.scenarios:
            return self.scenarios[-1].steps
        return []


# DISABLED: class FeatureBuilder(# XXX_JE_DISABLED: BuilderSequenceView,
# DISABLED: pylint: disable=too-many-ancestors
class FeatureBuilder(ManyScenariosBuilder,
                     ManyRulesBuilderMixin,
                     BuilderOperationsMixin):

    def __init__(self, feature=None, **container_kwargs):
        if feature is None:
            self._feature = self.make_feature(**container_kwargs)
        elif isinstance(feature, Feature):
            self._feature = feature
        else:
            raise TypeError("%r (expected: Feature)" % feature)

        super(FeatureBuilder, self).__init__(self.feature)
        # DISABLED: super(FeatureBuilder, self).__init__(builder=self,
        #                                                data=self.scenarios)

    @property
    def feature(self):
        return self._feature

    @property
    def rules(self):
        return self.feature.rules

    # @property
    # def filename(self):
    #     return self.feature.filename
    #
    # @property
    # def scenario_container(self):
    #     return self.feature
    #
    # @property
    # def scenarios(self):
    #     return self.feature.scenarios
    #
    # @property
    # def steps(self):
    #     if self.scenarios:
    #         return self.scenarios[-1].steps
    #     return []


# DISABLED: class ModelBuilder(BuilderSequenceView, ManyFeaturesBuilderMixin):
class ModelBuilder(BuilderOperationsMixin,
                   ManyFeaturesBuilderMixin):
    """Aka: ManyFeaturesBuilder"""
    def __init__(self):
        # DISABLED: super(ModelBuilder, self).__init__(self, [])
        super(ModelBuilder, self).__init__()
        self._features = []

    @property
    def features(self):
        return self._features

    @property
    def last_feature(self):
        if self.features:
            return self.features[-1]
        return self.make_feature()

    @property
    def filename(self):
        return self.last_feature.filename

    @property
    def rules(self):
        return self.last_feature.rules

    @property
    def scenarios(self):
        return self.last_feature.scenarios

    @property
    def steps(self):
        if self.scenarios:
            return self.scenarios[-1].steps
        return []
