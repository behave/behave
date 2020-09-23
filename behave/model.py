# -*- coding: utf-8 -*-
# pylint: disable=too-many-lines
"""
This module provides the model element class that represent a behave model:

* :class:`Feature`
* :class:`Scenario`
* :class:`ScenarioOutline`
* :class:`Step`
* ...
"""

from __future__ import absolute_import, with_statement, print_function
import copy
import difflib
import logging
import itertools
import time
import six
from six.moves import zip       # pylint: disable=redefined-builtin
from behave.model_core import \
        Status, BasicStatement, TagAndStatusStatement, TagStatement, Replayable
from behave.matchers import NoMatch
from behave.textutil import text as _text
if six.PY2:
    # -- USE PYTHON3 BACKPORT: With unicode traceback support.
    import traceback2 as traceback
else:
    import traceback


# ---------------------------------------------------------------------------
# MODEL UTILITIES:
# ---------------------------------------------------------------------------
def reset_steps(steps):
    for step in steps:
        step.reset()
    return steps


def copy_steps(steps):
    """Copy steps; needed if steps should be used in multiple run contexts.

    :param steps:       List of steps to copy.
    :return: List of copied steps.
    """
    return [copy.copy(step) for step in steps]


def copy_and_reset_steps(steps):
    """Copy steps and reset each step (status, duration, etc.)

    :param steps:       List of steps to copy.
    :return: List of copied steps.
    """
    return reset_steps(copy_steps(steps))


# ---------------------------------------------------------------------------
# MODEL CLASSES:
# ---------------------------------------------------------------------------
class ScenarioContainer(TagAndStatusStatement, Replayable):
    """Abstract base class for model elements
    that contains the following structure:

    .. code-block:: gherkin

        @tag1 @tag2
        ScenarioContainer: ...
            DescriptionLine?
            Background?
            Scenario*
            ScenarioOutline*

    Applicable to:

    * :class:`Feature`
    * :class:`Rule`

    .. seealso:: Gherkin grammar
        https://github.com/cucumber/cucumber/.../gherkin/gherkin.berp

    The attributes are:

    .. attribute:: keyword

       This is the keyword as seen in the *feature file*.
       In English this will be "Feature" or "Rule".

    .. attribute:: name

       The name (or title) of the model entity (the text after the keyword.)

    .. attribute:: description

       The description of the feature as seen in the *feature file*. This is
       stored as a list of text lines.

    .. attribute:: background

       The :class:`~behave.model.Background` for this feature, if any.

    .. attribute:: run_items

       An ordered list of Rule, Scenario or ScenarioOutline items.
       Only features can contain Rule items.

    .. attribute:: scenarios

       A list of :class:`~behave.model.Scenario` making up this feature.

    .. attribute:: tags

       A list of @tags (as :class:`~behave.model.Tag` which are basically
       glorified strings) attached to the feature.
       See :ref:`controlling things with tags`.

    .. attribute:: status

       Read-Only. A summary status of the feature's run. If read before the
       feature is fully tested it will return "untested" otherwise it will
       return one of:

       Status.untested
         The feature was has not been completely tested yet.

       Status.skipped
         The execution of this model entity (feature or rule)
         should be / was skipped (excluded from the test run).

       Status.passed
         The model entity (feature or rule) was tested successfully.

       Status.failed
         One or more run items of this model entity failed.

       .. versionchanged:: 1.2.6
            Use Status enum class (was: string).

    .. attribute:: duration

       The time, in seconds, that it took to test this feature. If read before
       the feature is tested it will return 0.0.

    .. attribute:: hook_failed

        Indicates if a hook failure occured while running this feature.

    .. attribute:: filename

       The file name (or "<string>") of the *feature file* where the feature
       was found.

    .. attribute:: line

       The line number of the *feature file* where the feature was found.
    """
    type = "feature_or_rule"

    def __init__(self, filename, line, keyword, name, tags=None,
                 description=None, scenarios=None, background=None):
        tags = tags or []
        super(ScenarioContainer, self).__init__(filename, line, keyword, name, tags)
        self.description = description or []
        self.hook_failed = False
        self.run_starttime = 0
        self.run_endtime = 0
        self.run_items = []     # CASE: Rule, Scenario, ScenarioOutline
        self.scenarios = []
        self.background = background
        if scenarios:
            for scenario in scenarios:
                self.add_scenario(scenario)

    def reset(self):
        """Reset to clean state before a test run."""
        super(ScenarioContainer, self).reset()
        self.hook_failed = False
        self.run_starttime = 0
        self.run_endtime = 0
        for run_item in self.run_items:
            run_item.reset()

    def _setup_context_for_run(self, context):
        """Setup/Init runner context for run."""
        # -- OVERRIDDEN: By derived classes.
        pass

    def __iter__(self):
        return iter(self.run_items)

    def add_scenario(self, scenario):
        feature = getattr(self, "feature", None)
        if isinstance(self, Feature):
            feature = self

        scenario.parent = self
        scenario.feature = feature
        scenario.background = self.background
        self.scenarios.append(scenario)
        self.run_items.append(scenario)

    def compute_status(self):
        """Compute the status of this feature based on its:
          * scenarios
          * scenario outlines
          * hook failures

        :return: Computed status (as string-enum).
        """
        if self.hook_failed:
            return Status.failed

        skipped = True
        passed_count = 0
        for run_item in self.run_items:
            run_item_status = run_item.status
            if run_item_status == Status.failed:
                return Status.failed
            elif run_item_status == Status.untested:
                if passed_count > 0:
                    return Status.failed  # ABORTED: Some passed, now untested.
                return Status.untested
            if run_item_status != Status.skipped:
                skipped = False
            if run_item_status == Status.passed:
                passed_count += 1

        if skipped:
            return Status.skipped
        # -- OTHERWISE:
        return Status.passed

    @property
    def duration(self):
        # -- NEW: Background is executed N times, now part of scenarios.
        # TODO: Use self.run_endtime - self.run_starttime
        feature_duration = 0.0
        # -- OLD IMPLEMENTATION:
        for scenario in self.scenarios:
            feature_duration += scenario.duration
        # -- NEW IMPLEMENTATION:
        # feature_duration = self.run_endtime - self.run_starttime
        return feature_duration

    def walk_scenarios(self, with_outlines=False, with_rules=False):
        """Provides a flat list of all scenarios of this ScenarioContainer.
        A ScenarioOutline element adds its scenarios to this list.
        But the ScenarioOutline element itself is only added when specified.

        A flat scenario list is useful when all scenarios of a features
        should be processed.

        :param with_outlines: If ScenarioOutline items should be added, too.
        :return: List of all scenarios of this feature.
        """
        all_scenarios = []
        for run_item in self.run_items:
            if isinstance(run_item, Rule):
                rule = run_item
                if with_rules:
                    all_scenarios.append(rule)
                scenarios = rule.walk_scenarios(with_outlines=with_outlines)
                all_scenarios.extend(scenarios)
            elif isinstance(run_item, ScenarioOutline):
                scenario_outline = run_item
                if with_outlines:
                    all_scenarios.append(scenario_outline)
                all_scenarios.extend(scenario_outline.scenarios)
            else:
                assert isinstance(run_item, Scenario), "OOPS: %r" % run_item
                all_scenarios.append(run_item)
        return all_scenarios

    def iter_scenarios(self):
        return iter(self.walk_scenarios())

    def iter_scenario_outlines(self):
        return iter([x for x in self.walk_scenarios(with_outlines=True)
                     if isinstance(x, ScenarioOutline)])

    def iter_rules(self):
        return iter([x for x in self.run_items if isinstance(x, Rule)])

    def should_run(self, config=None):
        """
        Determines if this Feature (and its scenarios) should run.
        Implements the run decision logic for a feature.
        The decision depends on:

          * if the Feature is marked as skipped
          * if the config.tag_expression enable/disable this feature

        :param config:  Runner configuration to use (optional).
        :return: True, if scenario should run. False, otherwise.
        """
        answer = not self.should_skip
        if answer and config:
            answer = self.should_run_with_tags(config.tag_expression)
        return answer

    def should_run_with_tags(self, tag_expression):
        """Determines if this feature should run when the tag expression is used.
        A feature should run if:
          * it should run according to its tags
          * any of its scenarios should run according to its tags

        :param tag_expression:  Runner/config environment tags to use.
        :return: True, if feature should run. False, otherwise (skip it).
        """
        run_feature = tag_expression.check(self.tags)
        if not run_feature:
            for scenario in self:
                if scenario.should_run_with_tags(tag_expression):
                    run_feature = True
                    break
        return run_feature

    def mark_skipped(self):
        """Marks this feature (and all its scenarios and steps) as skipped.
        Note this function may be called before the feature is executed.
        """
        self.skip(require_not_executed=True)
        assert self.status == Status.skipped or self.hook_failed

    def skip(self, reason=None, require_not_executed=False):
        """Skip executing this model entity or the remaining parts of it.
        Note that this model entity (feature or rule) may be already partly
        executed when this function is called.

        :param reason:  Optional reason why feature should be skipped (as string).
        :param require_not_executed: Optional, requires that feature is not
                        executed yet (default: false).
        """
        if reason:
            entity_name = self.type.upper()
            logger = logging.getLogger("behave")
            logger.warning(u"SKIP %s %s: %s", entity_name, self.name, reason)

        self.clear_status()
        self.should_skip = True
        self.skip_reason = reason
        for run_item in self.run_items:
            run_item.skip(reason, require_not_executed)
        if not self.run_items:
            # -- SPECIAL CASE: Feature without scenarios
            self.set_status(Status.skipped)
        assert self.status in self.final_status #< skipped, failed or passed.

    def run(self, runner):
        """Run ScenarioContainer with its scenarios.

        :param runner:  Runner to use.
        :return: True, if test-run failed.
        """
        # pylint: disable=too-many-branches, too-many-locals, too-many-statements
        # MAYBE: self.reset()
        self.clear_status()
        self.hook_failed = False
        self.run_starttime = time.time()

        entity_name = self.type # VALUE: "feature" or "rule"
        hook_before_entity = "before_{0}".format(entity_name)
        hook_after_entity = "after_{0}".format(entity_name)

        runner.context._push(layer=entity_name)      # pylint: disable=protected-access
        runner.context.tags = set(self.tags)
        self._setup_context_for_run(runner.context)

        skip_entity_untested = runner.aborted
        should_run_entity = self.should_run(runner.config)
        failed_count = 0
        hooks_called = False
        if not runner.config.dry_run and should_run_entity:
            hooks_called = True
            for tag in self.tags:
                runner.run_hook("before_tag", runner.context, tag)
            runner.run_hook(hook_before_entity, runner.context, self)
            if self.hook_failed:
                failed_count += 1

            # -- RE-EVALUATE SHOULD-RUN STATE:
            # Hook may call entity.mark_skipped() to exclude it.
            skip_entity_untested = self.hook_failed or runner.aborted
            should_run_entity = self.should_run()

        # run this entity if the tags say so or any one of its scenarios
        if should_run_entity or runner.config.show_skipped:
            for formatter in runner.formatters:
                formatter_callback = getattr(formatter, entity_name, None)
                if formatter_callback:
                    formatter_callback(self)
            if self.background:
                for formatter in runner.formatters:
                    formatter.background(self.background)

        if not skip_entity_untested:
            # -- RUN: Rules, Scenarios or ScenarioOutlines
            for run_item in self.run_items:
                # -- OPTIONAL: Select scenario by name (regular expressions).
                should_run_with_name = \
                    getattr(run_item, "should_run_with_name_select", None)
                if (runner.config.name and should_run_with_name and
                        not should_run_with_name(runner.config)):
                    run_item.mark_skipped()
                    continue

                failed = run_item.run(runner)
                if failed:
                    failed_count += 1
                    if runner.config.stop or runner.aborted:
                        # -- FAIL-EARLY: Stop after first failure.
                        break

        self.clear_status()  # -- ENFORCE: compute_status() after run.
        if not self.run_items and not should_run_entity:
            # -- SPECIAL CASE: Feature without scenarios
            self.set_status(Status.skipped)

        if hooks_called:
            runner.run_hook(hook_after_entity, runner.context, self)
            for tag in self.tags:
                runner.run_hook("after_tag", runner.context, tag)
            if self.hook_failed:
                failed_count += 1
                self.set_status(Status.failed)

        # -- PERFORM CONTEXT CLEANUP: May raise cleanup errors.
        try:
            runner.context._pop()       # pylint: disable=protected-access
        except Exception:               # pylint: disable=broad-except
            # -- CLEANUP-ERROR:
            self.set_status(Status.failed)

        if should_run_entity or runner.config.show_skipped:
            callback_name = "{0}_finished".format(entity_name)
            if entity_name == "feature":
                callback_name = "eof"

            for formatter in runner.formatters:
                formatter_callback = getattr(formatter, callback_name, None)
                if formatter_callback:
                    formatter_callback()

        self.run_endtime = time.time()
        failed = (failed_count > 0)
        return failed


class Feature(ScenarioContainer):
    """A `feature`_ parsed from a *feature file*.

    The attributes are:

    .. attribute:: keyword

       This is the keyword as seen in the *feature file*. In English this will
       be "Feature".

    .. attribute:: name

       The name of the feature (the text after "Feature".)

    .. attribute:: description

       The description of the feature as seen in the *feature file*. This is
       stored as a list of text lines.

    .. attribute:: background

       The :class:`~behave.model.Background` for this feature, if any.

    .. attribute:: scenarios

       A list of :class:`~behave.model.Scenario` making up this feature.

    .. attribute:: tags

       A list of @tags (as :class:`~behave.model.Tag` which are basically
       glorified strings) attached to the feature.
       See :ref:`controlling things with tags`.

    .. attribute:: status

       Read-Only. A summary status of the feature's run. If read before the
       feature is fully tested it will return "untested" otherwise it will
       return one of:

       Status.untested
         The feature was has not been completely tested yet.
       Status.skipped
         One or more steps of this feature was passed over during testing.
       Status.passed
         The feature was tested successfully.
       Status.failed
         One or more steps of this feature failed.

       .. versionchanged:: 1.2.6
            Use Status enum class (was: string).

    .. attribute:: hook_failed

        Indicates if a hook failure occured while running this feature.

        .. versionadded:: 1.2.6

    .. attribute:: duration

       The time, in seconds, that it took to test this feature. If read before
       the feature is tested it will return 0.0.

    .. attribute:: filename

       The file name (or "<string>") of the *feature file* where the feature
       was found.

    .. attribute:: line

       The line number of the *feature file* where the feature was found.

    .. attribute:: language

       Indicates which spoken language (English, French, German, ..) was used
       for parsing the feature file and its keywords. The I18N language code
       indicates which language is used. This corresponds to the language tag
       at the beginning of the feature file.

       .. versionadded:: 1.2.6

    .. _`feature`: gherkin.html#features
    """

    type = "feature"

    def __init__(self, filename, line, keyword, name, tags=None,
                 description=None, scenarios=None, background=None,
                 language=None):
        tags = tags or []
        super(Feature, self).__init__(filename, line, keyword, name, tags,
                                      description, scenarios, background)
        self.rules = []
        self.language = language
        self.parser = None

    def __repr__(self):
        return '<Feature "%s": %s run items, %d rules, %d scenarios>' % \
            (self.name, len(self.run_items),
             len(self.rules), len(self.scenarios))

    def _setup_context_for_run(self, context):
        context.feature = self

    def add_background(self, background):
        self.background = background
        self.background.parent = self

    def add_rule(self, rule):
        """Add a rule to this feature (supported in: Gherkin v6).

        .. versionadded: 1.2.7
        """
        feature = self
        rule.parent = feature
        rule.feature = feature
        self.rules.append(rule)
        self.run_items.append(rule)
        if self.background:
            # -- ENSURE: Rule inherits feature.background.
            if not rule.background:
                # -- ENSURE: Rule has a default background.
                # Necessary to inherit feature.background (or disable it).
                rule_default_background = Background(rule.filename, rule.line)
                rule.add_background(rule_default_background)
            rule.background.inherited_background = self.background


class Rule(ScenarioContainer):
    """A `rule`_ parsed from a *feature file*.

    .. code-block:: gherkin

        # -- FILE: *.feature
        Feature: ...
            Description....

            Background?
            Scenario*
            ScenarioOutline*

            @tag1 @tag2
            Rule: Some Rule Title
              Description?      # CARDINALITY: 0..1 (optional).
              Background?       # CARDINALITY: 0..1 (optional).
              Scenario*         # CARDINALITY: 0..N (many)
              ScenarioOutline*  # CARDINALITY: 0..N (many)

    The attributes are:

    .. attribute:: keyword

       This is the keyword as seen in the *feature file*. In English this will
       be "Feature".

    .. attribute:: name

       The name of the feature (the text after "Feature".)

    .. attribute:: description

       The description of the feature as seen in the *feature file*. This is
       stored as a list of text lines.

    .. attribute:: background

       The :class:`~behave.model.Background` for this feature, if any.

    .. attribute:: scenarios

       A list of :class:`~behave.model.Scenario` making up this feature.

    .. attribute:: tags

       A list of @tags (as :class:`~behave.model.Tag` which are basically
       glorified strings) attached to the feature.
       See :ref:`controlling things with tags`.

    .. attribute:: status

       Read-Only. A summary status of the feature's run. If read before the
       feature is fully tested it will return "untested" otherwise it will
       return one of:

       Status.untested
         The feature was has not been completely tested yet.
       Status.skipped
         One or more steps of this feature was passed over during testing.
       Status.passed
         The feature was tested successfully.
       Status.failed
         One or more steps of this feature failed.

       .. versionchanged:: 1.2.6
            Use Status enum class (was: string).

    .. attribute:: hook_failed

        Indicates if a hook failure occured while running this feature.

        .. versionadded:: 1.2.6

    .. attribute:: duration

       The time, in seconds, that it took to test this feature. If read before
       the feature is tested it will return 0.0.

    .. attribute:: filename

       The file name (or "<string>") of the *feature file* where the feature
       was found.

    .. attribute:: line

       The line number of the *feature file* where the feature was found.

    .. attribute:: language

       Indicates which spoken language (English, French, German, ..) was used
       for parsing the feature file and its keywords. The I18N language code
       indicates which language is used. This corresponds to the language tag
       at the beginning of the feature file.


    .. versionadded:: 1.2.7
    .. _`rule`: gherkin.html#rule
    """
    type = "rule"

    def __init__(self, filename, line, keyword, name, tags=None,
                 description=None, scenarios=None, background=None,
                 parent=None):
        tags = tags or []
        super(Rule, self).__init__(filename, line, keyword, name, tags,
                                   description, scenarios, background)
        self.parent = parent
        self.feature = parent
        self._use_background_inheritance = True

    def _setup_context_for_run(self, context):
        context.rule = self

    def __repr__(self):
        return '<Rule "%s": %d scenario(s)>' % \
            (self.name, len(self.scenarios))

    def add_background(self, background, inherited=None):
        if inherited is None:
            feature = self.feature or self.parent
            inherited = feature.background

        self.background = background
        self.background.inherited_background = inherited
        self.background.use_inheritance = self.use_background_inheritance
        self.background.parent = self
        # -- ENSURE: Normally background is added before scenarios.
        for scenario in self.walk_scenarios():
            scenario.background = self.background

    @property
    def use_background_inheritance(self):
        return self._use_background_inheritance

    @use_background_inheritance.setter
    def use_background_inheritance(self, value):
        self._use_background_inheritance = value
        if self.background:
            self.background.use_inheritance = value


class Background(BasicStatement, Replayable):
    """A `background`_ parsed from a *feature file*.

    Behaviour:

    * Each scenario of a scenario container (Feature, Rule)
      inherits the Background of its scenario container
    * Background steps in a scenario are executed before scenario steps
    * Rule Background inherits the Feature Background (outer background) if any
    * Inherited Background steps are used/executed first
    * Optionally, background inheritance can be disabled
      (normally: by using a fixture/fixture-tag)

    The attributes are:

    .. attribute:: keyword

       This is the keyword as seen in the *feature file*. In English this will
       typically be "Background".

    .. attribute:: name

       The name of the background (the text after "Background:".)

    .. attribute:: steps

       A list of :class:`~behave.model.Step` making up this background.

    .. attribute:: duration

       The time, in seconds, that it took to run this background. If read
       before the background is run it will return 0.0.

    .. attribute:: filename

       The file name (or "<string>") of the *feature file* where the background
       was found.

    .. attribute:: line

       The line number of the *feature file* where the background was found.

    .. attribute:: description

       Optional description (text, as list of lines).

       .. versionadded:: 1.2.7 (supported since Gherkin v6 or earlier)

    .. _`background`: gherkin.html#backgrounds
    """
    type = "background"

    def __init__(self, filename, line, keyword=u"Background", name=u"",
                 steps=None, description=None):
        super(Background, self).__init__(filename, line, keyword, name)
        self.description = description or []
        self.steps = steps or []
        self.inherited_background = None
        self._inherited_steps = None
        self._use_inheritance = True

    @property
    def use_inheritance(self):
        """Indicates if this Background should inherit from an outer Background.
        Background inheritance mechanism is enabled (per default).
        Optionally, this mechanism can be disabled (or overridden).

        :return: Current background inheritance state (as bool).

        .. versionadded:: 1.2.7
        """
        return self._use_inheritance

    @use_inheritance.setter
    def use_inheritance(self, value):
        """Enable/disable background inheritance mechanism for this Background.

        :param value:   New value (as bool).

        .. versionadded:: 1.2.7
        """
        # -- ENSURE: inherited_steps are reinitialized (later).
        self._use_inheritance = bool(value)
        self._inherited_steps = None

    @property
    def inherited_steps(self):
        # versionadded:: 1.2.7
        if self._inherited_steps is None:
            # -- LAZY-INIT: Support enable/disable the inheritance mechanism.
            steps = []
            if self.inherited_background and self._use_inheritance:
                steps = copy_and_reset_steps(self.inherited_background.steps)
            self._inherited_steps = steps
        return self._inherited_steps

    def iter_steps(self):
        """Returns iterator to all steps, including inherited steps (if any).

        .. versionadded:: 1.2.7
        """
        if self.inherited_steps:
            return itertools.chain(self.inherited_steps, self.steps)
        return iter(self.steps)

    @property
    def all_steps(self):
        return self.iter_steps()

    @property
    def duration(self):
        duration = 0
        for step in self.steps:
            duration += step.duration
        return duration

    def __repr__(self):
        return '<Background "%s">' % self.name

    def __iter__(self):
        return self.iter_steps()


class Scenario(TagAndStatusStatement, Replayable):
    """A `scenario`_ parsed from a *feature file*.

    The attributes are:

    .. attribute:: keyword

       This is the keyword as seen in the *feature file*. In English this will
       typically be "Scenario".

    .. attribute:: name

       The name of the scenario (the text after "Scenario:".)

    .. attribute:: description

       The description of the scenario as seen in the *feature file*.
       This is stored as a list of text lines.

    .. attribute:: feature

       The :class:`~behave.model.Feature` this scenario belongs to.

    .. attribute:: steps

       A list of :class:`~behave.model.Step` making up this scenario.

    .. attribute:: tags

       A list of @tags (as :class:`~behave.model.Tag` which are basically
       glorified strings) attached to the scenario.
       See :ref:`controlling things with tags`.

    .. attribute:: status

       Read-Only. A summary status of the scenario's run. If read before the
       scenario is fully tested it will return "untested" otherwise it will
       return one of:


       Status.untested
         The scenario was has not been completely tested yet.
       Status.skipped
         One or more steps of this scenario was passed over during testing.
       Status.passed
         The scenario was tested successfully.
       Status.failed
         One or more steps of this scenario failed.

       .. versionchanged:: 1.2.6
            Use Status enum class (was: string)

    .. attribute:: hook_failed

        Indicates if a hook failure occured while running this scenario.

        .. versionadded:: 1.2.6

    .. attribute:: duration

       The time, in seconds, that it took to test this scenario. If read before
       the scenario is tested it will return 0.0.

    .. attribute:: filename

       The file name (or "<string>") of the *feature file* where the scenario
       was found.

    .. attribute:: line

       The line number of the *feature file* where the scenario was found.

    .. attribute:: parent

        Points to parent entity that contains this scenario (Feature, Rule, ...).

        .. versionadded:: 1.2.7

    .. _`scenario`: gherkin.html#scenarios
    """
    # pylint: disable=too-many-instance-attributes
    type = "scenario"
    continue_after_failed_step = False

    def __init__(self, filename, line, keyword, name, tags=None, steps=None,
                 description=None, parent=None):
        tags = tags or []
        super(Scenario, self).__init__(filename, line, keyword, name, tags,
                                       parent=parent)
        self.description = description or []
        self.steps = steps or []
        self.background = None
        self.feature = None  # REFER-TO: owner=Feature
        self.hook_failed = False
        self._background_steps = None
        self._use_background = True
        self._row = None
        self.was_dry_run = False

    def reset(self):
        """Reset the internal data to reintroduce new-born state just after the
        ctor was called.
        """
        super(Scenario, self).reset()
        self.hook_failed = False
        self._row = None
        self.was_dry_run = False
        for step in self.all_steps:
            step.reset()

    @property
    def use_background(self):
        """Indicates if the background is/would be used (if any exists).
        NOTE: The Background (steps) are normally used.

        .. versionadded:: 1.2.7
        """
        return self._use_background

    @use_background.setter
    def use_background(self, value):
        """Enable/disable the usage of the background (steps).

        :param value:  New value (as bool).

        .. versionadded:: 1.2.7
        """
        # -- ENSURE: background_steps are reinitialized.
        self._use_background = value
        self._background_steps = None

    @property
    def background_steps(self):
        """Provide background steps if feature/rule has a background.
        Lazy init that copies the background steps.

        Note that a copy of the background steps is needed to ensure
        that the background step status is specific to the scenario.

        :return:  List of background steps or empty list
        """
        if self._background_steps is None:
            # -- LAZY-INIT (need copy of background.steps):
            # Each scenario needs own background.steps.
            # Otherwise, background step status of the last-run scenario is used.
            steps = []
            if self.background and self.use_background:
                steps = copy_and_reset_steps(self.background.all_steps)
            self._background_steps = steps
        return self._background_steps

    def iter_steps(self):
        """Returns iterator to all steps, including background steps if any.

        .. versionadded:: 1.2.7
        """
        if self.background is not None:
            return itertools.chain(self.background_steps, self.steps)
        return iter(self.steps)

    @property
    def all_steps(self):
        return self.iter_steps()

    def __repr__(self):
        return '<Scenario "%s">' % self.name

    def __iter__(self):
        return self.iter_steps()

    def compute_status(self):
        """Compute the status of the scenario from its steps
        (and hook failures).

        :return: Computed status (as enum value).
        """
        if self.hook_failed:
            return Status.failed

        for step in self.all_steps:
            if step.status == Status.undefined:
                if self.was_dry_run:
                    # -- SPECIAL CASE: In dry-run with undefined-step discovery
                    #    Undefined steps should not cause failed scenario.
                    return Status.untested
                # -- NORMALLY: Undefined steps cause failed scenario.
                return Status.failed
            elif step.status != Status.passed:
                # pylint: disable=line-too-long
                assert step.status in (Status.failed, Status.skipped, Status.untested)
                return step.status
        return Status.passed

    @property
    def duration(self):
        # -- ORIG: for step in self.steps:  Background steps were excluded.
        scenario_duration = 0
        for step in self.all_steps:
            scenario_duration += step.duration
        return scenario_duration

    @property
    def effective_tags(self):
        """
        Effective tags for this scenario:
          * own tags
          * tags inherited from its feature
        """
        tags = self.tags
        if self.feature:
            tags = self.feature.tags + self.tags
        return tags

    def should_run(self, config=None):
        """
        Determines if this Scenario (or ScenarioOutline) should run.
        Implements the run decision logic for a scenario.
        The decision depends on:

          * if the Scenario is marked as skipped
          * if the config.tag_expression enable/disable this scenario
          * if the scenario is selected by name

        :param config:  Runner configuration to use (optional).
        :return: True, if scenario should run. False, otherwise.
        """
        answer = not self.should_skip
        if answer and config:
            answer = (self.should_run_with_tags(config.tag_expression) and
                      self.should_run_with_name_select(config))
        return answer

    def should_run_with_tags(self, tag_expression):
        """Checks if scenario should run when the tag expression is used.

        :param tag_expression:  Runner/config environment tags to use.
        :return: True, if scenario should run. False, otherwise (skip it).
        """
        return tag_expression.check(self.effective_tags)

    def should_run_with_name_select(self, config):
        """Checks if scenario should run when it is selected by name.

        :param config:  Runner/config environment name regexp (if any).
        :return: True, if scenario should run. False, otherwise (skip it).
        """
        # -- SELECT-ANY: If select by name is not specified (not config.name).
        return not config.name or config.name_re.search(self.name)

    def mark_skipped(self):
        """Marks this scenario (and all its steps) as skipped.
        Note that this method can be called before the scenario is executed.
        """
        self.skip(require_not_executed=True)
        assert self.status == Status.skipped or self.hook_failed, \
               "OOPS: scenario.status=%s" % self.status.name

    def skip(self, reason=None, require_not_executed=False):
        """Skip from executing this scenario or the remaining parts of it.
        Note that the scenario may be already partly executed
        when this method is called.

        :param reason:  Optional reason why it should be skipped (as string).
        """
        if reason:
            scenario_type = self.__class__.__name__
            logger = logging.getLogger("behave")
            logger.warning(u"SKIP %s %s: %s", scenario_type, self.name, reason)

        self.clear_status()
        self.should_skip = True
        self.skip_reason = reason
        for step in self.all_steps:
            not_executed = step.status in (Status.untested, Status.skipped)
            if not_executed:
                step.status = Status.skipped
            else:
                assert not require_not_executed, \
                    "REQUIRE NOT-EXECUTED, but step is %s" % step.status

        scenario_without_steps = not self.steps and not self.background_steps
        if scenario_without_steps:
            self.set_status(Status.skipped)
        assert self.status in self.final_status #< skipped, failed or passed

    def run(self, runner):
        # pylint: disable=too-many-branches, too-many-statements
        self.clear_status()
        self.captured.reset()
        self.hook_failed = False
        failed = False
        skip_scenario_untested = runner.aborted
        run_scenario = self.should_run(runner.config)
        run_steps = run_scenario and not runner.config.dry_run
        dry_run_scenario = run_scenario and runner.config.dry_run
        self.was_dry_run = dry_run_scenario

        runner.context._push(layer="scenario")      # pylint: disable=protected-access
        runner.context.scenario = self
        runner.context.tags = set(self.effective_tags)

        hooks_called = False
        if not runner.config.dry_run and run_scenario:
            hooks_called = True
            for tag in self.tags:
                runner.run_hook("before_tag", runner.context, tag)
            runner.run_hook("before_scenario", runner.context, self)
            if self.hook_failed:
                # -- SKIP: Scenario steps and behave like dry_run_scenario
                failed = True

            # -- RE-EVALUATE SHOULD-RUN STATE:
            # Hook may call scenario.mark_skipped() to exclude it.
            skip_scenario_untested = self.hook_failed or runner.aborted
            run_scenario = self.should_run()
            run_steps = run_scenario and not runner.config.dry_run

        if run_scenario or runner.config.show_skipped:
            for formatter in runner.formatters:
                formatter.scenario(self)

        # TODO: Reevaluate location => Move in front of hook-calls
        runner.setup_capture()

        if run_scenario or runner.config.show_skipped:
            for step in self:
                for formatter in runner.formatters:
                    formatter.step(step)

        if not skip_scenario_untested:
            for step in self.all_steps:
                if run_steps:
                    if not step.run(runner):
                        # -- CASE: Failed or undefined step
                        #    Optionally continue_after_failed_step if enabled.
                        #    But disable run_steps after undefined-step.
                        run_steps = (self.continue_after_failed_step and
                                     step.status == Status.failed)
                        failed = True
                        # pylint: disable=protected-access
                        runner.context._set_root_attribute("failed", True)
                        self.set_status(Status.failed)
                    elif self.should_skip:
                        # -- CASE: Step skipped remaining scenario.
                        # assert self.status == Status.skipped
                        run_steps = False
                elif failed or dry_run_scenario:
                    # -- SKIP STEPS: After failure/undefined-step occurred.
                    # BUT: Detect all remaining undefined steps.
                    step.status = Status.skipped
                    if dry_run_scenario:
                        step.status = Status.untested
                    found_step_match = runner.step_registry.find_match(step)
                    if not found_step_match:
                        step.status = Status.undefined
                        runner.undefined_steps.append(step)
                    elif dry_run_scenario:
                        # -- BETTER DIAGNOSTICS: Provide step file location
                        # (when --format=pretty is used).
                        assert step.status == Status.untested
                        for formatter in runner.formatters:
                            # -- EMULATE: Step.run() protocol w/o step execution.
                            formatter.match(found_step_match)
                            formatter.result(step)
                else:
                    # -- SKIP STEPS: For disabled scenario.
                    # CASES:
                    #   * Undefined steps are not detected (by intention).
                    #   * Step skipped remaining scenario.
                    step.status = Status.skipped

        self.clear_status()  # -- ENFORCE: compute_status() after run.
        if not run_scenario and not self.steps:
            # -- SPECIAL CASE: Scenario without steps.
            self.set_status(Status.skipped)


        if hooks_called:
            runner.run_hook("after_scenario", runner.context, self)
            for tag in self.tags:
                runner.run_hook("after_tag", runner.context, tag)
            if self.hook_failed:
                self.set_status(Status.failed)
                failed = True

        # -- PERFORM CONTEXT-CLEANUP: May raise cleanup errors.
        try:
            runner.context._pop()       # pylint: disable=protected-access
        except Exception:               # pylint: disable=broad-except
            self.set_status(Status.failed)
            failed = True

        # -- CAPTURED-OUTPUT:
        store_captured = (runner.config.junit or self.status == Status.failed)
        if store_captured:
            self.captured = runner.capture_controller.captured

        runner.teardown_capture()
        return failed


class ScenarioOutlineBuilder(object):
    """Helper class to use a ScenarioOutline as a template and
    build its scenarios (as template instances).
    """
    annotation_schema = u"{name} -- @{row.id} {examples.name}"

    def __init__(self, annotation_schema=None):
        if annotation_schema is None:
            annotation_schema = self.__class__.annotation_schema
        self.annotation_schema = annotation_schema

    @staticmethod
    def render_template(text, row=None, params=None):
        """Render a text template with placeholders, ala "Hello <name>".

        :param row:     As placeholder provider (dict-like).
        :param params:  As additional placeholder provider (as dict).
        :return: Rendered text, known placeholders are substituted w/ values.
        """
        if not ("<" in text and ">" in text):
            return text

        safe_values = False
        for placeholders in (row, params):
            if not placeholders:
                continue
            for name, value in placeholders.items():
                if safe_values and ("<" in value and ">" in value):
                    continue    # -- OOPS, value looks like placeholder.
                placeholder = u"<%s>" % name
                text = text.replace(placeholder, value)
        return text

    def make_scenario_name(self, outline_name, example, row, params=None):
        """Build a scenario name for an example row of this scenario outline.
        Placeholders for row data are replaced by values.

        SCHEMA: "{outline_name} -*- {examples.name}@{row.id}"

        :param outline_name:    ScenarioOutline's name (as template).
        :param example:         Examples object.
        :param row:             Row of this example.
        :param params:          Additional placeholders for example/row.
        :return: Computed name for the scenario representing example/row.
        """
        if params is None:
            params = {}
        params["examples.name"] = example.name or ""
        params.setdefault("examples.index", example.index)
        params.setdefault("row.index", row.index)
        params.setdefault("row.id", row.id)

        # -- STEP: Replace placeholders in scenario/example name (if any).
        examples_name = self.render_template(example.name, row, params)
        params["examples.name"] = examples_name
        scenario_name = self.render_template(outline_name, row, params)

        class Data(object):
            def __init__(self, name, index):
                self.name = name
                self.index = index
                self.id = name      # pylint: disable=invalid-name

        example_data = Data(examples_name, example.index)
        row_data = Data(row.id, row.index)
        return self.annotation_schema.format(name=scenario_name,
                                             examples=example_data, row=row_data)

    @classmethod
    def make_row_tags(cls, outline_tags, row, params=None):
        if not outline_tags:
            return []

        tags = []
        for tag in outline_tags:
            if "<" in tag and ">" in tag:
                tag = cls.render_template(tag, row, params)
            if "<" in tag or ">" in tag:
                # -- OOPS: Unknown placeholder, drop tag.
                continue
            new_tag = Tag.make_name(tag, unescape=True)
            tags.append(new_tag)
        return tags

    @classmethod
    def make_step_for_row(cls, outline_step, row, params=None):
        # -- BASED-ON: new_step = outline_step.set_values(row)
        new_step = copy.deepcopy(outline_step)
        new_step.name = cls.render_template(new_step.name, row, params)
        if new_step.text:
            new_step.text = cls.render_template(new_step.text, row)
        if new_step.table:
            for name, value in row.items():
                placeholder = u"<%s>" % name
                for i, cell in enumerate(new_step.table.headings):
                    new_step.table.headings[i] = cell.replace(placeholder, value)
                for step_row in new_step.table:
                    for i, cell in enumerate(step_row.cells):
                        step_row.cells[i] = cell.replace(placeholder, value)
        return new_step

    def build_scenarios(self, scenario_outline):
        """Build scenarios for a ScenarioOutline from its examples."""
        # -- BUILD SCENARIOS (once): For this ScenarioOutline from examples.
        params = {
            "examples.name": None,
            "examples.index": None,
            "row.index": None,
            "row.id": None,
        }
        scenarios = []
        for example_index, example in enumerate(scenario_outline.examples):
            example.index = example_index+1
            params["examples.name"] = example.name
            params["examples.index"] = _text(example.index)
            if not example.table:
                # -- SYNDROME: Examples keyword without table
                print("ERROR: ScenarioOutline.Examples: Has NO-TABLE syndrome ({0})"\
                      .format(example.location))
                continue

            for row_index, row in enumerate(example.table):
                row.index = row_index+1
                row.id = "%d.%d" % (example.index, row.index)
                params["row.id"] = row.id
                params["row.index"] = _text(row.index)
                scenario_name = self.make_scenario_name(scenario_outline.name,
                                                        example, row, params)
                row_tags = self.make_row_tags(scenario_outline.tags, row, params)
                row_tags.extend(example.tags)
                new_steps = []
                for outline_step in scenario_outline.steps:
                    new_step = self.make_step_for_row(outline_step, row, params)
                    new_steps.append(new_step)

                # -- STEP: Make Scenario name for this row.
                # scenario_line = example.line + 2 + row_index
                scenario_line = row.line
                scenario = Scenario(scenario_outline.filename, scenario_line,
                                    scenario_outline.keyword,
                                    scenario_name, row_tags, new_steps)
                scenario.feature = scenario_outline.feature
                scenario.parent = scenario_outline
                scenario.background = scenario_outline.background
                scenario.description = scenario_outline.description
                scenario._row = row     # pylint: disable=protected-access
                scenarios.append(scenario)
        return scenarios


class ScenarioOutline(Scenario):
    """A `scenario outline`_ parsed from a *feature file*.

    A scenario outline extends the existing :class:`~behave.model.Scenario`
    class with the addition of the :class:`~behave.model.Examples` tables of
    data from the *feature file*.

    The attributes are:

    .. attribute:: keyword

       This is the keyword as seen in the *feature file*. In English this will
       typically be "Scenario Outline".

    .. attribute:: name

       The name of the scenario (the text after "Scenario Outline:".)

    .. attribute:: description

       The description of the `scenario outline`_ as seen in the *feature file*.
       This is stored as a list of text lines.

    .. attribute:: feature

       The :class:`~behave.model.Feature` this scenario outline belongs to.

    .. attribute:: steps

       A list of :class:`~behave.model.Step` making up this scenario outline.

    .. attribute:: examples

       A list of :class:`~behave.model.Examples` used by this scenario outline.

    .. attribute:: tags

       A list of @tags (as :class:`~behave.model.Tag` which are basically
       glorified strings) attached to the scenario.
       See :ref:`controlling things with tags`.

    .. attribute:: status

       Read-Only. A summary status of the scenario outlines's run. If read
       before the scenario is fully tested it will return "untested" otherwise
       it will return one of:

       Status.untested
         The scenario was has not been completely tested yet.
       Status.skipped
         One or more scenarios of this outline was passed over during testing.
       Status.passed
         The scenario was tested successfully.
       Status.failed
         One or more scenarios of this outline failed.

        .. versionchanged:: 1.2.6
            Use Status enum class (was: string)

    .. attribute:: duration

       The time, in seconds, that it took to test the scenarios of this
       outline. If read before the scenarios are tested it will return 0.0.

    .. attribute:: filename

       The file name (or "<string>") of the *feature file* where the scenario
       was found.

    .. attribute:: line

       The line number of the *feature file* where the scenario was found.

    .. _`scenario outline`: gherkin.html#scenario-outlines
    """
    type = "scenario_outline"
    annotation_schema = ScenarioOutlineBuilder.annotation_schema

    def __init__(self, filename, line, keyword, name, tags=None,
                 steps=None, examples=None, description=None):
        super(ScenarioOutline, self).__init__(filename, line, keyword, name,
                                              tags, steps, description)
        self.examples = examples or []
        self._scenarios = []

    def reset(self):
        """Reset runtime temporary data like before a test run."""
        super(ScenarioOutline, self).reset()
        for scenario in self._scenarios:    # -- AVOID: BUILD-SCENARIOS
            scenario.reset()

    @property
    def scenarios(self):
        """Return the scenarios with the steps altered to take the values from
        the examples.
        """
        if self._scenarios:
            return self._scenarios

        # -- BUILD SCENARIOS (once): For this ScenarioOutline from examples.
        builder = ScenarioOutlineBuilder(self.annotation_schema)
        self._scenarios = builder.build_scenarios(self)
        return self._scenarios

    def __repr__(self):
        return '<ScenarioOutline "%s">' % self.name

    def __iter__(self):
        return iter(self.scenarios) # -- REQUIRE: BUILD-SCENARIOS

    def compute_status(self):
        skipped_count = 0
        for scenario in self._scenarios:    # -- AVOID: BUILD-SCENARIOS
            scenario_status = scenario.status
            if scenario_status in (Status.failed, Status.untested):
                return scenario_status
            elif scenario_status == Status.skipped:
                skipped_count += 1
        if skipped_count > 0 and skipped_count == len(self._scenarios):
            # -- ALL SKIPPED:
            return Status.skipped
        # -- OTHERWISE: ALL PASSED (some scenarios may have been excluded)
        return Status.passed

    @property
    def duration(self):
        outline_duration = 0
        for scenario in self._scenarios:    # -- AVOID: BUILD-SCENARIOS
            outline_duration += scenario.duration
        return outline_duration

    def should_run_with_tags(self, tag_expression):
        """Determines if this scenario outline (or one of its scenarios)
        should run when the tag expression is used.

        :param tag_expression:  Runner/config environment tags to use.
        :return: True, if scenario should run. False, otherwise (skip it).
        """
        if tag_expression.check(self.effective_tags):
            return True

        for scenario in self.scenarios:     # -- REQUIRE: BUILD-SCENARIOS
            if scenario.should_run_with_tags(tag_expression):
                return True
        # -- NOTHING SELECTED:
        return False

    def should_run_with_name_select(self, config):
        """Determines if this scenario should run when it is selected by name.

        :param config:  Runner/config environment name regexp (if any).
        :return: True, if scenario should run. False, otherwise (skip it).
        """
        if not config.name:
            return True # -- SELECT-ALL: Select by name is not specified.

        for scenario in self.scenarios:     # -- REQUIRE: BUILD-SCENARIOS
            if scenario.should_run_with_name_select(config):
                return True
        # -- NOTHING SELECTED:
        return False


    def mark_skipped(self):
        """Marks this scenario outline (and all its scenarios/steps) as skipped.
        Note that this method may be called before the scenario outline
        is executed.
        """
        self.skip(require_not_executed=True)
        assert self.status == Status.skipped

    def skip(self, reason=None, require_not_executed=False):
        """Skip from executing this scenario outline or its remaining parts.
        Note that the scenario outline may be already partly executed
        when this method is called.

        :param reason:  Optional reason why it should be skipped (as string).
        """
        if reason:
            logger = logging.getLogger("behave")
            logger.warning(u"SKIP ScenarioOutline %s: %s", self.name, reason)

        self.clear_status()
        self.should_skip = True
        for scenario in self.scenarios:
            scenario.skip(reason, require_not_executed)
        if not self.scenarios:
            # -- SPECIAL CASE: ScenarioOutline without scenarios/examples
            self.set_status(Status.skipped)
        assert self.status in self.final_status #< skipped, failed or passed

    def run(self, runner):
        # pylint: disable=protected-access
        # REASON: context._set_root_attribute(), scenario._row
        self.clear_status()
        failed_count = 0
        for scenario in self.scenarios:     # -- REQUIRE: BUILD-SCENARIOS
            runner.context._set_root_attribute("active_outline", scenario._row)
            failed = scenario.run(runner)
            if failed:
                failed_count += 1
                if runner.config.stop or runner.aborted:
                    # -- FAIL-EARLY: Stop after first failure.
                    break
        runner.context._set_root_attribute("active_outline", None)
        return failed_count > 0

class Examples(TagStatement, Replayable):
    """A table parsed from a `scenario outline`_ in a *feature file*.

    The attributes are:

    .. attribute:: keyword

       This is the keyword as seen in the *feature file*. In English this will
       typically be "Example".

    .. attribute:: name

       The name of the example (the text after "Example:".)

    .. attribute:: table

       An instance  of :class:`~behave.model.Table` that came with the example
       in the *feature file*.

    .. attribute:: filename

       The file name (or "<string>") of the *feature file* where the example
       was found.

    .. attribute:: line

       The line number of the *feature file* where the example was found.

    .. _`examples`: gherkin.html#examples
    """
    type = "examples"

    def __init__(self, filename, line, keyword, name, tags=None, table=None):
        super(Examples, self).__init__(filename, line, keyword, name, tags)
        self.table = table
        self.index = None


class Step(BasicStatement, Replayable):
    """A single `step`_ parsed from a *feature file*.

    The attributes are:

    .. attribute:: keyword

       This is the keyword as seen in the *feature file*. In English this will
       typically be "Given", "When", "Then" or a number of other words.

    .. attribute:: name

       The name of the step (the text after "Given" etc.)

    .. attribute:: step_type

       The type of step as determined by the keyword. If the keyword is "and"
       then the previous keyword in the *feature file* will determine this
       step's step_type.

    .. attribute:: text

       An instance of :class:`~behave.model.Text` that came with the step
       in the *feature file*.

    .. attribute:: table

       An instance of :class:`~behave.model.Table` that came with the step
       in the *feature file*.

    .. attribute:: status

       Read-Only. A summary status of the step's run. If read before the
       step is tested it will return "untested" otherwise it will
       return one of:

       Status.untested
         This step was not run (yet).
       Status.skipped
         This step was skipped during testing.
       Status.passed
         The step was tested successfully.
       Status.failed
         The step failed.
       Status.undefined
         The step has no matching step implementation.

       .. versionchanged::
            Use Status enum class (was: string).

    .. attribute:: hook_failed

        Indicates if a hook failure occured while running this step.

        .. versionadded:: 1.2.6

    .. attribute:: duration

       The time, in seconds, that it took to test this step. If read before the
       step is tested it will return 0.0.

    .. attribute:: error_message

       If the step failed then this will hold any error information, as a
       single string. It will otherwise be None.

       .. versionchanged:: 1.2.6 (moved to base class)

    .. attribute:: filename

       The file name (or "<string>") of the *feature file* where the step was
       found.

    .. attribute:: line

       The line number of the *feature file* where the step was found.

    .. _`step`: gherkin.html#steps
    """
    type = "step"

    def __init__(self, filename, line, keyword, step_type, name, text=None,
                 table=None):
        super(Step, self).__init__(filename, line, keyword, name)
        self.step_type = step_type
        self.text = text
        self.table = table

        self.status = Status.untested
        self.hook_failed = False
        self.duration = 0

    def reset(self):
        """Reset temporary runtime data to reach clean state again."""
        super(Step, self).reset()
        self.status = Status.untested
        self.hook_failed = False
        self.duration = 0
        # -- POSTCONDITION: assert self.status == Status.untested

    def __repr__(self):
        return '<%s "%s">' % (self.step_type, self.name)

    def __eq__(self, other):
        return (self.step_type, self.name) == (other.step_type, other.name)

    def __hash__(self):
        return hash(self.step_type) + hash(self.name)

    def set_values(self, table_row):
        """Clone a new step from this one, used for ScenarioOutline.
        Replace ScenarioOutline placeholders w/ values.

        :param table_row:  Placeholder data for example row.
        :return: Cloned, adapted step object.

        .. note:: Deprecating
            Use 'ScenarioOutlineBuilder.make_step_for_row()' instead.
        """
        import warnings
        warnings.warn("Use 'ScenarioOutline.make_step_for_row()' instead",
                      PendingDeprecationWarning, stacklevel=2)
        outline_step = self
        return ScenarioOutlineBuilder.make_step_for_row(outline_step, table_row)

    def run(self, runner, quiet=False, capture=True):
        # pylint: disable=too-many-branches, too-many-statements
        # -- RESET: Run-time information.
        # self.status = Status.untested
        # self.hook_failed = False
        self.reset()

        match = runner.step_registry.find_match(self)
        if match is None:
            runner.undefined_steps.append(self)
            if not quiet:
                for formatter in runner.formatters:
                    formatter.match(NoMatch())

            self.status = Status.undefined
            if not quiet:
                for formatter in runner.formatters:
                    formatter.result(self)
            return False

        keep_going = True
        error = u""

        if not quiet:
            for formatter in runner.formatters:
                formatter.match(match)

        if capture:
            runner.start_capture()

        skip_step_untested = False
        runner.run_hook("before_step", runner.context, self)
        if self.hook_failed:
            skip_step_untested = True

        start = time.time()
        if not skip_step_untested:
            try:
                # -- ENSURE:
                #  * runner.context.text/.table attributes are reset (#66).
                #  * Even EMPTY multiline text is available in context.
                runner.context.text = self.text
                runner.context.table = self.table
                match.run(runner.context)
                if self.status == Status.untested:
                    # -- NOTE: Executed step may have skipped scenario and itself.
                    self.status = Status.passed
            except KeyboardInterrupt as e:
                runner.aborted = True
                error = u"ABORTED: By user (KeyboardInterrupt)."
                self.status = Status.failed
                self.store_exception_context(e)
            except AssertionError as e:
                self.status = Status.failed
                self.store_exception_context(e)
                if e.args:
                    message = _text(e)
                    error = u"Assertion Failed: "+ message
                else:
                    # no assertion text; format the exception
                    error = _text(traceback.format_exc())
            except Exception as e:      # pylint: disable=broad-except
                self.status = Status.failed
                error = _text(traceback.format_exc())
                self.store_exception_context(e)

        self.duration = time.time() - start
        runner.run_hook("after_step", runner.context, self)
        if self.hook_failed:
            self.status = Status.failed

        if capture:
            runner.stop_capture()

        # flesh out the failure with details
        store_captured_always = False   # PREPARED
        store_captured = self.status == Status.failed or store_captured_always
        if self.status == Status.failed:
            assert isinstance(error, six.text_type)
            if capture:
                # -- CAPTURE-ONLY: Non-nested step failures.
                self.captured = runner.capture_controller.captured
                error2 = self.captured.make_report()
                if error2:
                    error += "\n" + error2
            self.error_message = error
            keep_going = False
        elif store_captured and capture:
            self.captured = runner.capture_controller.captured

        if not quiet:
            for formatter in runner.formatters:
                formatter.result(self)

        return keep_going


class Table(Replayable):
    """A `table`_ extracted from a *feature file*.

    Table instance data is accessible using a number of methods:

    **iteration**
      Iterating over the Table will yield the :class:`~behave.model.Row`
      instances from the .rows attribute.

    **indexed access**
      Individual rows may be accessed directly by index on the Table instance;
      table[0] gives the first non-heading row and table[-1] gives the last
      row.

    The attributes are:

    .. attribute:: headings

       The headings of the table as a list of strings.

    .. attribute:: rows

       An list of instances of :class:`~behave.model.Row` that make up the body
       of the table in the *feature file*.

    Tables are also comparable, for what that's worth. Headings and row data
    are compared.

    .. _`table`: gherkin.html#table
    """
    type = "table"

    def __init__(self, headings, line=None, rows=None):
        Replayable.__init__(self)
        self.headings = headings
        self.line = line
        self.rows = []
        if rows:
            for row in rows:
                self.add_row(row, line)

    def add_row(self, row, line=None):
        self.rows.append(Row(self.headings, row, line))

    def add_column(self, column_name, values=None, default_value=u""):
        """Adds a new column to this table.
        Uses :param:`default_value` for new cells (if :param:`values` are
        not provided). param:`values` are extended with :param:`default_value`
        if values list is smaller than the number of table rows.

        :param column_name: Name of new column (as string).
        :param values: Optional list of cell values in new column.
        :param default_value: Default value for cell (if values not provided).
        :returns: Index of new column (as number).
        """
        # assert isinstance(column_name, unicode)
        assert not self.has_column(column_name)
        if values is None:
            values = [default_value] * len(self.rows)
        elif not isinstance(values, list):
            values = list(values)
        if len(values) < len(self.rows):
            more_size = len(self.rows) - len(values)
            more_values = [default_value] * more_size
            values.extend(more_values)

        new_column_index = len(self.headings)
        self.headings.append(column_name)
        for row, value in zip(self.rows, values):
            assert len(row.cells) == new_column_index
            row.cells.append(value)
        return new_column_index

    def remove_column(self, column_name):
        if not isinstance(column_name, int):
            try:
                column_index = self.get_column_index(column_name)
            except ValueError:
                raise KeyError("column=%s is unknown" % column_name)

        assert isinstance(column_index, int)
        assert column_index < len(self.headings)
        del self.headings[column_index]
        for row in self.rows:
            assert column_index < len(row.cells)
            del row.cells[column_index]

    def remove_columns(self, column_names):
        for column_name in column_names:
            self.remove_column(column_name)

    def has_column(self, column_name):
        return column_name in self.headings

    def get_column_index(self, column_name):
        return self.headings.index(column_name)

    def require_column(self, column_name):
        """Require that a column exists in the table.
        Raise an AssertionError if the column does not exist.

        :param column_name: Name of new column (as string).
        :return: Index of column (as number) if it exists.
        """
        if not self.has_column(column_name):
            columns = ", ".join(self.headings)
            msg = "REQUIRE COLUMN: %s (columns: %s)" % (column_name, columns)
            raise AssertionError(msg)
        return self.get_column_index(column_name)

    def require_columns(self, column_names):
        for column_name in column_names:
            self.require_column(column_name)

    def ensure_column_exists(self, column_name):
        """Ensures that a column with the given name exists.
        If the column does not exist, the column is added.

        :param column_name: Name of column (as string).
        :return: Index of column (as number).
        """
        if self.has_column(column_name):
            return self.get_column_index(column_name)
        return self.add_column(column_name)

    def __repr__(self):
        return "<Table: %dx%d>" % (len(self.headings), len(self.rows))

    def __eq__(self, other):
        if isinstance(other, Table):
            if self.headings != other.headings:
                return False
            for my_row, their_row in zip(self.rows, other.rows):
                if my_row != their_row:
                    return False
        else:
            # -- ASSUME: table <=> raw data comparison
            other_rows = other
            for my_row, their_row in zip(self.rows, other_rows):
                if my_row != their_row:
                    return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iter__(self):
        return iter(self.rows)

    def __getitem__(self, index):
        return self.rows[index]

    def assert_equals(self, data):
        """Assert that this table's cells are the same as the supplied "data".

        The data passed in must be a list of lists giving:

            [
                [row 1],
                [row 2],
                [row 3],
            ]

        If the cells do not match then a useful AssertionError will be raised.
        """
        assert self == data
        raise NotImplementedError


class Row(object):
    """One row of a `table`_ parsed from a *feature file*.

    Row data is accessible using a number of methods:

    **iteration**
      Iterating over the Row will yield the individual cells as strings.

    **named access**
      Individual cells may be accessed by heading name; row["name"] would give
      the cell value for the column with heading "name".

    **indexed access**
      Individual cells may be accessed directly by index on the Row instance;
      row[0] gives the first cell and row[-1] gives the last cell.

    The attributes are:

    .. attribute:: cells

       The list of strings that form the cells of this row.

    .. attribute:: headings

       The headings of the table as a list of strings.

    Rows are also comparable, for what that's worth. Only the cells are
    compared.

    .. _`table`: gherkin.html#table
    """
    def __init__(self, headings, cells, line=None, comments=None):
        self.headings = headings
        self.comments = comments
        for c in cells:
            assert isinstance(c, six.text_type)
        self.cells = cells
        self.line = line

    def __getitem__(self, name):
        try:
            index = self.headings.index(name)
        except ValueError:
            if isinstance(name, int):
                index = name
            else:
                raise KeyError('"%s" is not a row heading' % name)
        return self.cells[index]

    def __repr__(self):
        return "<Row %r>" % (self.cells,)

    def __eq__(self, other):
        return self.cells == other.cells

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return len(self.cells)

    def __iter__(self):
        return iter(self.cells)

    def items(self):
        return zip(self.headings, self.cells)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def as_dict(self):
        """Converts the row and its cell data into a dictionary.
        :return: Row data as dictionary (without comments, line info).
        """
        from behave.compat.collections import OrderedDict
        return OrderedDict(self.items())


class Tag(six.text_type):
    """Tags appear may be associated with Features or Scenarios.

    They're a subclass of regular strings (unicode pre-Python 3) with an
    additional ``line`` number attribute (where the tag was seen in the source
    feature file.

    See :ref:`controlling things with tags`.
    """
    allowed_chars = u"._-=:,;()"    # In addition to aplha-numerical chars.
    quoting_chars = ("'", '"', "<", ">")

    def __new__(cls, name, line):
        o = six.text_type.__new__(cls, name)
        o.line = line
        return o

    @classmethod
    def make_name(cls, text, unescape=False, allowed_chars=None):
        """Translate text into a "valid tag" without whitespace, etc.

        Translation rules are:
          * alnum chars => same, kept
          * space chars => "_"
          * other chars => deleted

        Preserve following characters (in addition to alnums, like: A-z, 0-9):
          * dots        => "." (support: dotted-names, active-tag name schema)
          * minus       => "-" (support: dashed-names)
          * underscore  => "_"
          * equal       => "=" (support: active-tag name schema)
          * colon       => ":" (support: active-tag name schema or similar)
          * semicolon   => ";" (support: complex tag notation)
          * comma       => "," (support: complex tag notation)
          * opening-parens  => "(" (support: complex tag notation)
          * closing-parens  => ")" (support: complex tag notation)

        :param text: Unicode text as input for name.
        :param unescape: Optional flag to unescape some chars (default: false)
        :param allowed_chars: Optional string with additional preserved chars.
        :return: Unicode name that can be used as tag.
        """
        assert isinstance(text, six.text_type)
        if allowed_chars is None:
            allowed_chars = cls.allowed_chars

        if unescape:
            # -- UNESCAPE: Some escaped sequences
            text = text.replace("\\t", "\t").replace("\\n", "\n")
        chars = []
        for char in text:
            if char.isalnum() or (allowed_chars and char in allowed_chars):
                chars.append(char)
            elif char.isspace():
                chars.append(u"_")
            elif char in cls.quoting_chars:
                pass    # -- NORMALIZE: Remove any quoting chars.
            # -- MAYBE:
            # else:
            #     # -- OTHERWISE: Accept gracefully any other character.
            #     chars.append(char)
        return u"".join(chars)


class Text(six.text_type):
    """Store multiline text from a Step definition.

    The attributes are:

    .. attribute:: value

       The actual text parsed from the *feature file*.

    .. attribute:: content_type

       Currently only "text/plain".
    """
    def __new__(cls, value, content_type=u"text/plain", line=0):
        assert isinstance(value, six.text_type)
        assert isinstance(content_type, six.text_type)
        o = six.text_type.__new__(cls, value)
        o.content_type = content_type
        o.line = line
        return o

    def line_range(self):
        line_count = len(self.splitlines())
        return (self.line, self.line + line_count + 1)

    def replace(self, old, new, count=-1):
        return Text(super(Text, self).replace(old, new, count), self.content_type,
                    self.line)

    def assert_equals(self, expected):
        """Assert that my text is identical to the "expected" text.

        A nice context diff will be displayed if they do not match.
        """
        if self == expected:
            return True
        diff = []
        for line in difflib.unified_diff(self.splitlines(),
                                         expected.splitlines()):
            diff.append(line)
        # strip unnecessary diff prefix
        diff = ["Text does not match:"] + diff[3:]
        raise AssertionError("\n".join(diff))


# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def reset_model(model_elements):
    """Reset the test run information stored in model elements.

    :param model_elements:  List of model elements (Feature, Scenario, ...)
    """
    for model_element in model_elements:
        model_element.reset()
