# -*- coding: utf-8 -*-

from __future__ import with_statement
import copy
import difflib
import itertools
import os.path
import time
import traceback
from behave import step_registry
from behave.compat.os_path import relpath


class Argument(object):
    '''An argument found in a *feature file* step name and extracted using
    step decorator `parameters`_.

    The attributes are:

    .. attribute:: original

       The actual text matched in the step name.

    .. attribute:: value

       The potentially type-converted value of the argument.

    .. attribute:: name

       The name of the argument. This will be None if the parameter is
       anonymous.

    .. attribute:: start

       The start index in the step name of the argument. Used for display.

    .. attribute:: end

       The end index in the step name of the argument. Used for display.
    '''
    def __init__(self, start, end, original, value, name=None):
        self.start = start
        self.end = end
        self.original = original
        self.value = value
        self.name = name


# @total_ordering
# class FileLocation(unicode):
class FileLocation(object):
    """
    Provides a value object for file location objects.
    A file location consists of:

      * filename
      * line (number), optional

    LOCATION SCHEMA:
      * "{filename}:{line}" or
      * "{filename}" (if line number is not present)
    """
    # -- pylint: disable=R0904,R0924
    #   R0904: 30,0:FileLocation: Too many public methods (43/30) => unicode
    #   R0924: 30,0:FileLocation: Badly implemented Container, ...=> unicode
    __pychecker__ = "missingattrs=line"     # -- Ignore warnings for 'line'.

    def __init__(self, filename, line=None):
        self.filename = filename
        self.line = line

    # def __new__(cls, filename, line=None):
    #     assert isinstance(filename, basestring)
    #     obj = unicode.__new__(cls, filename)
    #     obj.line = line
    #     obj.__filename = filename
    #     return obj
    #
    # @property
    # def filename(self):
    #     # -- PREVENT: Assignments via property (and avoid self-recursion).
    #     return self.__filename

    def get(self):
        return self.filename

    def abspath(self):
        return os.path.abspath(self.filename)

    def basename(self):
        return os.path.basename(self.filename)

    def dirname(self):
        return os.path.dirname(self.filename)

    def relpath(self, start=os.curdir):
        """
        Compute relative path for start to filename.

        :param start: Base path or start directory (default=current dir).
        :return: Relative path from start to filename
        """
        return relpath(self.filename, start)

    def exists(self):
        return os.path.exists(self.filename)

    def __eq__(self, other):
        if isinstance(other, FileLocation):
            return self.filename == other.filename and self.line == other.line
        elif isinstance(other, basestring):
            return self.filename == other
        else:
            raise AttributeError("Cannot compare FileLocation with %s:%s" % \
                                 (type(other), other))

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        if isinstance(other, FileLocation):
            if self.filename < other.filename:
                return True
            elif self.filename > other.filename:
                return False
            else:
                assert self.filename == other.filename
                return self.line < other.line
        elif isinstance(other, basestring):
            return self.filename < other
        else:
            raise AttributeError("Cannot compare FileLocation with %s:%s" % \
                                 (type(other), other))

    def __le__(self, other):
        # -- SEE ALSO: python2.7, functools.total_ordering
        return not other < self

    def __gt__(self, other):
        # -- SEE ALSO: python2.7, functools.total_ordering
        if isinstance(other, FileLocation):
            return other < self
        else:
            return self.filename > other

    def __ge__(self, other):
        # -- SEE ALSO: python2.7, functools.total_ordering
        return not self < other

    def __repr__(self):
        return u'<FileLocation: filename="%s", line=%s>' % \
               (self.filename, self.line)

    def __str__(self):
        if self.line is None:
            return self.filename
        return u"%s:%d" % (self.filename, self.line)


class BasicStatement(object):
    def __init__(self, filename, line, keyword, name):
        filename = filename or '<string>'
        filename = relpath(filename, os.getcwd())   # -- NEEDS: abspath?
        self.location = FileLocation(filename, line)
        assert isinstance(keyword, unicode)
        assert isinstance(name, unicode)
        self.keyword = keyword
        self.name = name

    @property
    def filename(self):
        # return os.path.abspath(self.location.filename)
        return self.location.filename

    @property
    def line(self):
        return self.location.line

    # @property
    # def location(self):
    #     p = relpath(self.filename, os.getcwd())
    #     return '%s:%d' % (p, self.line)

    def __cmp__(self, other):
        # -- NOTE: Ignore potential FileLocation differences.
        return cmp((self.keyword, self.name), (other.keyword, other.name))


class TagStatement(BasicStatement):

    def __init__(self, filename, line, keyword, name, tags):
        super(TagStatement, self).__init__(filename, line, keyword, name)
        self.tags = tags


class TagAndStatusStatement(BasicStatement):
    final_status = ('passed', 'failed', 'skipped')

    def __init__(self, filename, line, keyword, name, tags):
        super(TagAndStatusStatement, self).__init__(filename, line, keyword, name)
        self.tags = tags
        self.should_skip = False
        self._cached_status = None

    @property
    def status(self):
        if self._cached_status not in self.final_status:
            # -- RECOMPUTE: As long as final status is not reached.
            self._cached_status = self.compute_status()
        return self._cached_status

    def reset(self):
        self.should_skip = False
        self._cached_status = None

    def compute_status(self):
        raise NotImplementedError


class Replayable(object):
    type = None

    def replay(self, formatter):
        getattr(formatter, self.type)(self)


class Feature(TagAndStatusStatement, Replayable):
    '''A `feature`_ parsed from a *feature file*.

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
       glorified strings) attached to the feature. See `controlling
       things with tags`_.

    .. attribute:: status

       Read-Only. A summary status of the feature's run. If read before the
       feature is fully tested it will return "untested" otherwise it will
       return one of:

       "untested"
         The feature was has not been completely tested yet.
       "skipped"
         One or more steps of this feature was passed over during testing.
       "passed"
         The feature was tested successfully.
       "failed"
         One or more steps of this feature failed.

    .. attribute:: duration

       The time, in seconds, that it took to test this feature. If read before
       the feature is tested it will return 0.0.

    .. attribute:: filename

       The file name (or "<string>") of the *feature file* where the feature
       was found.

    .. attribute:: line

       The line number of the *feature file* where the feature was found.

    .. _`feature`: gherkin.html#features
    '''

    type = "feature"

    def __init__(self, filename, line, keyword, name, tags=[], description=[],
                 scenarios=[], background=None):
        super(Feature, self).__init__(filename, line, keyword, name, tags)
        self.description = description or []
        self.scenarios = []
        self.background = background
        self.parser = None
        for scenario in scenarios:
            self.add_scenario(scenario)

    def reset(self):
        '''
        Reset to clean state before a test run.
        '''
        super(Feature, self).reset()
        for scenario in self.scenarios:
            scenario.reset()

    def __repr__(self):
        return '<Feature "%s": %d scenario(s)>' % \
            (self.name, len(self.scenarios))

    def __iter__(self):
        return iter(self.scenarios)

    def add_scenario(self, scenario):
        scenario.feature = self
        scenario.background = self.background
        self.scenarios.append(scenario)

    def compute_status(self):
        """
        Compute the status of this feature based on its:
           * scenarios
           * scenario outlines

        :return: Computed status (as string-enum).
        """
        skipped = True
        passed_count = 0
        for scenario in self.scenarios:
            scenario_status = scenario.status
            if scenario_status == 'failed':
                return 'failed'
            elif scenario_status == 'untested':
                if passed_count > 0:
                    return 'failed'  # ABORTED: Some passed, now untested.
                return 'untested'
            if scenario_status != 'skipped':
                skipped = False
            if scenario_status == 'passed':
                passed_count += 1
        return skipped and 'skipped' or 'passed'

    @property
    def duration(self):
        if self.background:
            feature_duration = self.background.duration or 0.0
        else:
            feature_duration = 0.0
        for scenario in self.scenarios:
            feature_duration += scenario.duration
        return feature_duration

    def walk_scenarios(self, with_outlines=False):
        """
        Provides a flat list of all scenarios of this feature.
        A ScenarioOutline element adds its scenarios to this list.
        But the ScenarioOutline element itself is only added when specified.

        A flat scenario list is useful when all scenarios of a features
        should be processed.

        :param with_outlines: If ScenarioOutline items should be added, too.
        :return: List of all scenarios of this feature.
        """
        all_scenarios = []
        for scenario in self.scenarios:
            if isinstance(scenario, ScenarioOutline):
                scenario_outline = scenario
                if with_outlines:
                    all_scenarios.append(scenario_outline)
                all_scenarios.extend(scenario_outline.scenarios)
            else:
                all_scenarios.append(scenario)
        return all_scenarios

    def should_run(self, config=None):
        """
        Determines if this Feature (and its scenarios) should run.
        Implements the run decision logic for a feature.
        The decision depends on:

          * if the Feature is marked as skipped
          * if the config.tags (tag expression) enable/disable this feature

        :param config:  Runner configuration to use (optional).
        :return: True, if scenario should run. False, otherwise.
        """
        answer = not self.should_skip
        if answer and config:
            answer = self.should_run_with_tags(config.tags)
        return answer

    def should_run_with_tags(self, tag_expression):
        '''
        Determines if this feature should run when the tag expression is used.
        A feature should run if:
          * it should run according to its tags
          * any of its scenarios should run according to its tags

        :param tag_expression:  Runner/config environment tags to use.
        :return: True, if feature should run. False, otherwise (skip it).
        '''
        run_feature = tag_expression.check(self.tags)
        if not run_feature:
            for scenario in self:
                if scenario.should_run_with_tags(tag_expression):
                    run_feature = True
                    break
        return run_feature

    def mark_skipped(self):
        """
        Marks this feature (and all its scenarios and steps) as skipped.
        """
        self._cached_status = None
        self.should_skip = True
        for scenario in self.scenarios:
            scenario.mark_skipped()
        assert self.status == "skipped"

    def run(self, runner):
        self._cached_status = None
        runner.context._push()
        runner.context.feature = self

        # run this feature if the tags say so or any one of its scenarios
        run_feature = self.should_run(runner.config)
        if run_feature or runner.config.show_skipped:
            for formatter in runner.formatters:
                formatter.feature(self)

        # current tags as a set
        runner.context.tags = set(self.tags)

        if not runner.config.dry_run and run_feature:
            for tag in self.tags:
                runner.run_hook('before_tag', runner.context, tag)
            runner.run_hook('before_feature', runner.context, self)

        if self.background and (run_feature or runner.config.show_skipped):
            for formatter in runner.formatters:
                formatter.background(self.background)

        failed_count = 0
        for scenario in self:
            # -- OPTIONAL: Select scenario by name (regular expressions).
            if (runner.config.name and
                    not runner.config.name_re.search(scenario.name)):
                scenario.mark_skipped()
                continue

            failed = scenario.run(runner)
            if failed:
                failed_count += 1
                if runner.config.stop or runner.aborted:
                    # -- FAIL-EARLY: Stop after first failure.
                    break

        if run_feature:
            runner.run_hook('after_feature', runner.context, self)
            for tag in self.tags:
                runner.run_hook('after_tag', runner.context, tag)

        runner.context._pop()

        if run_feature or runner.config.show_skipped:
            for formatter in runner.formatters:
                formatter.eof()

        failed = (failed_count > 0)
        return failed


class Background(BasicStatement, Replayable):
    '''A `background`_ parsed from a *feature file*.

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

       The file name (or "<string>") of the *feature file* where the scenario
       was found.

    .. attribute:: line

       The line number of the *feature file* where the scenario was found.

    .. _`background`: gherkin.html#backgrounds
    '''
    type = "background"

    def __init__(self, filename, line, keyword, name, steps=[]):
        super(Background, self).__init__(filename, line, keyword, name)
        self.steps = steps or []

    def __repr__(self):
        return '<Background "%s">' % self.name

    def __iter__(self):
        return iter(self.steps)

    @property
    def duration(self):
        duration = 0
        for step in self.steps:
            duration += step.duration
        return duration


class Scenario(TagAndStatusStatement, Replayable):
    '''A `scenario`_ parsed from a *feature file*.

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
       glorified strings) attached to the scenario. See `controlling
       things with tags`_.

    .. attribute:: status

       Read-Only. A summary status of the scenario's run. If read before the
       scenario is fully tested it will return "untested" otherwise it will
       return one of:

       "untested"
         The scenario was has not been completely tested yet.
       "skipped"
         One or more steps of this scenario was passed over during testing.
       "passed"
         The scenario was tested successfully.
       "failed"
         One or more steps of this scenario failed.

    .. attribute:: duration

       The time, in seconds, that it took to test this scenario. If read before
       the scenario is tested it will return 0.0.

    .. attribute:: filename

       The file name (or "<string>") of the *feature file* where the scenario
       was found.

    .. attribute:: line

       The line number of the *feature file* where the scenario was found.

    .. _`scenario`: gherkin.html#scenarios
    '''
    type = "scenario"

    def __init__(self, filename, line, keyword, name, tags=[], steps=[],
                 description=None):
        super(Scenario, self).__init__(filename, line, keyword, name, tags)
        self.description = description or []
        self.steps = steps or []
        self.background = None
        self.feature = None  # REFER-TO: owner=Feature
        self._background_steps = None
        self._row = None
        self.was_dry_run = False
        self.stderr = None
        self.stdout = None

    def reset(self):
        '''
        Reset the internal data to reintroduce new-born state just after the
        ctor was called.
        '''
        super(Scenario, self).reset()
        self._row = None
        self.was_dry_run = False
        self.stderr = None
        self.stdout = None
        for step in self.all_steps:
            step.reset()

    @property
    def background_steps(self):
        '''
        Provide background steps if feature has a background.
        Lazy init that copies the background steps.

        Note that a copy of the background steps is needed to ensure
        that the background step status is specific to the scenario.

        :return:  List of background steps or empty list
        '''
        if self._background_steps is None:
            # -- LAZY-INIT (need copy of background.steps):
            # Each scenario needs own background.steps status.
            # Otherwise, background step status of the last scenario is used.
            steps = []
            if self.background:
                steps = [copy.copy(step) for step in self.background.steps]
            self._background_steps = steps
        return self._background_steps

    @property
    def all_steps(self):
        """Returns iterator to all steps, including background steps if any."""
        if self.background is not None:
            return itertools.chain(self.background_steps, self.steps)
        else:
            return iter(self.steps)

    def __repr__(self):
        return '<Scenario "%s">' % self.name

    def __iter__(self):
        # XXX return iter(self.all_steps)
        return self.all_steps

    def compute_status(self):
        """Compute the status of the scenario from its steps.
        :return: Computed status (as string).
        """
        for step in self.all_steps:
            if step.status == 'undefined':
                if self.was_dry_run:
                    # -- SPECIAL CASE: In dry-run with undefined-step discovery
                    #    Undefined steps should not cause failed scenario.
                    return 'untested'
                else:
                    # -- NORMALLY: Undefined steps cause failed scenario.
                    return 'failed'
            elif step.status != 'passed':
                assert step.status in ('failed', 'skipped', 'untested')
                return step.status
            #elif step.status == 'failed':
            #    return 'failed'
            #elif step.status == 'skipped':
            #    return 'skipped'
            #elif step.status == 'untested':
            #    return 'untested'
        return 'passed'

    @property
    def duration(self):
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
          * if the config.tags (tag expression) enable/disable this scenario

        :param config:  Runner configuration to use (optional).
        :return: True, if scenario should run. False, otherwise.
        """
        answer = not self.should_skip
        if answer and config:
            answer = self.should_run_with_tags(config.tags)
        return answer

    def should_run_with_tags(self, tag_expression):
        """
        Determines if this scenario should run when the tag expression is used.

        :param tag_expression:  Runner/config environment tags to use.
        :return: True, if scenario should run. False, otherwise (skip it).
        """
        return tag_expression.check(self.effective_tags)

    def mark_skipped(self):
        """
        Marks this scenario (and all its steps) as skipped.
        """
        self._cached_status = None
        self.should_skip = True
        for step in self.all_steps:
            assert step.status == "untested" or step.status == "skipped"
            step.status = "skipped"
        assert self.status == "skipped", "OOPS: scenario.status=%s" % self.status

    def run(self, runner):
        self._cached_status = None
        failed = False
        run_scenario = self.should_run(runner.config)
        run_steps = run_scenario and not runner.config.dry_run
        dry_run_scenario = run_scenario and runner.config.dry_run
        self.was_dry_run = dry_run_scenario

        if run_scenario or runner.config.show_skipped:
            for formatter in runner.formatters:
                formatter.scenario(self)

        runner.context._push()
        runner.context.scenario = self
        runner.context.tags = set(self.effective_tags)

        if not runner.config.dry_run and run_scenario:
            for tag in self.tags:
                runner.run_hook('before_tag', runner.context, tag)
            runner.run_hook('before_scenario', runner.context, self)

        runner.setup_capture()

        if run_scenario or runner.config.show_skipped:
            for step in self:
                for formatter in runner.formatters:
                    formatter.step(step)

        for step in self.all_steps:
            if run_steps:
                if not step.run(runner):
                    run_steps = False
                    failed = True
                    runner.context._set_root_attribute('failed', True)
                    self._cached_status = 'failed'
            elif failed or dry_run_scenario:
                # -- SKIP STEPS: After failure/undefined-step occurred.
                # BUT: Detect all remaining undefined steps.
                step.status = 'skipped'
                if dry_run_scenario:
                    step.status = 'untested'
                found_step = step_registry.registry.find_match(step)
                if not found_step:
                    step.status = 'undefined'
                    runner.undefined.append(step)
            else:
                # -- SKIP STEPS: For disabled scenario.
                # NOTE: Undefined steps are not detected (by intention).
                step.status = 'skipped'

        # Attach the stdout and stderr if generate Junit report
        if runner.config.junit:
            self.stdout = runner.context.stdout_capture.getvalue()
            self.stderr = runner.context.stderr_capture.getvalue()
        runner.teardown_capture()

        if not runner.config.dry_run and run_scenario:
            runner.run_hook('after_scenario', runner.context, self)
            for tag in self.tags:
                runner.run_hook('after_tag', runner.context, tag)

        runner.context._pop()
        return failed


class ScenarioOutline(Scenario):
    '''A `scenario outline`_ parsed from a *feature file*.

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
       glorified strings) attached to the scenario. See `controlling
       things with tags`_.

    .. attribute:: status

       Read-Only. A summary status of the scenario outlines's run. If read
       before the scenario is fully tested it will return "untested" otherwise
       it will return one of:

       "untested"
         The scenario was has not been completely tested yet.
       "skipped"
         One or more scenarios of this outline was passed over during testing.
       "passed"
         The scenario was tested successfully.
       "failed"
         One or more scenarios of this outline failed.

    .. attribute:: duration

       The time, in seconds, that it took to test the scenarios of this
       outline. If read before the scenarios are tested it will return 0.0.

    .. attribute:: filename

       The file name (or "<string>") of the *feature file* where the scenario
       was found.

    .. attribute:: line

       The line number of the *feature file* where the scenario was found.

    .. _`scenario outline`: gherkin.html#scenario-outlines
    '''
    type = "scenario_outline"

    def __init__(self, filename, line, keyword, name, tags=[],
                 steps=[], examples=[], description=None):
        super(ScenarioOutline, self).__init__(filename, line, keyword, name,
                                              tags, steps, description)
        self.examples = examples or []
        self._scenarios = []

    def reset(self):
        '''
        Reset runtime temporary data like before a test run.
        '''
        super(ScenarioOutline, self).reset()
        for scenario in self.scenarios:
            scenario.reset()

    @property
    def scenarios(self):
        '''Return the scenarios with the steps altered to take the values from
        the examples.
        '''
        if self._scenarios:
            return self._scenarios

        for example in self.examples:
            for row in example.table:
                new_steps = []
                for step in self.steps:
                    new_steps.append(step.set_values(row))
                scenario = Scenario(self.filename, self.line, self.keyword,
                                    self.name, self.tags, new_steps)
                scenario.feature = self.feature
                scenario.background = self.background
                scenario._row = row
                self._scenarios.append(scenario)
        return self._scenarios

    def __repr__(self):
        return '<ScenarioOutline "%s">' % self.name

    def __iter__(self):
        return iter(self.scenarios)

    def compute_status(self):
        for scenario in self.scenarios:
            scenario_status = scenario.status
            if scenario_status != 'passed':
                assert scenario_status in ('failed', 'skipped', 'untested')
                return scenario_status
            #if scenario.status == 'failed':
            #    return 'failed'
            #elif scenario.status == 'skipped':
            #    return 'skipped'
            #elif scenario.status == 'untested':
            #    return 'untested'
        return 'passed'

    @property
    def duration(self):
        outline_duration = 0
        for scenario in self.scenarios:
            outline_duration += scenario.duration
        return outline_duration

    def mark_skipped(self):
        """
        Marks this scenario outline (and all its scenarios/steps) as skipped.
        """
        self._cached_status = None
        self.should_skip = True
        for scenario in self.scenarios:
            scenario.mark_skipped()
        assert self.status == "skipped"

    def run(self, runner):
        self._cached_status = None
        failed_count = 0
        for scenario in self.scenarios:
            runner.context._set_root_attribute('active_outline', scenario._row)
            failed = scenario.run(runner)
            if failed:
                failed_count += 1
                if runner.config.stop or runner.aborted:
                    # -- FAIL-EARLY: Stop after first failure.
                    break
        runner.context._set_root_attribute('active_outline', None)
        return failed_count > 0


class Examples(BasicStatement, Replayable):
    '''A table parsed from a `scenario outline`_ in a *feature file*.

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

       The file name (or "<string>") of the *feature file* where the scenario
       was found.

    .. attribute:: line

       The line number of the *feature file* where the scenario was found.

    .. _`examples`: gherkin.html#examples
    '''
    type = "examples"

    def __init__(self, filename, line, keyword, name, table=None):
        super(Examples, self).__init__(filename, line, keyword, name)
        self.table = table


class Step(BasicStatement, Replayable):
    '''A single `step`_ parsed from a *feature file*.

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

       "skipped"
         This step was passed over during testing.
       "passed"
         The step was tested successfully.
       "failed"
         The step failed.

    .. attribute:: duration

       The time, in seconds, that it took to test this step. If read before the
       step is tested it will return 0.0.

    .. attribute:: error_message

       If the step failed then this will hold any error information, as a
       single string. It will otherwise be None.

    .. attribute:: filename

       The file name (or "<string>") of the *feature file* where the step was
       found.

    .. attribute:: line

       The line number of the *feature file* where the step was found.

    .. _`step`: gherkin.html#steps
    '''
    type = "step"

    def __init__(self, filename, line, keyword, step_type, name, text=None,
                 table=None):
        super(Step, self).__init__(filename, line, keyword, name)
        self.step_type = step_type
        self.text = text
        self.table = table

        self.status = 'untested'
        self.duration = 0.0
        self.error_message = None
        self.exception = None

    def reset(self):
        '''Reset temporary runtime data to reach clean state again.'''
        self.status = 'untested'
        self.duration = 0.0
        self.error_message = None
        self.exception = None

    def __repr__(self):
        return '<%s "%s">' % (self.step_type, self.name)

    def __eq__(self, other):
        return (self.step_type, self.name) == (other.step_type, other.name)

    def __hash__(self):
        return hash(self.step_type) + hash(self.name)

    def set_values(self, table_row):
        result = copy.deepcopy(self)
        for name, value in table_row.items():
            result.name = result.name.replace("<%s>" % name, value)
            if result.text:
                result.text = result.text.replace("<%s>" % name, value)
            if result.table:
                for row in result.table:
                    for i, cell in enumerate(row.cells):
                        row.cells[i] = cell.replace("<%s>" % name, value)
        return result

    def run(self, runner, quiet=False, capture=True):
        # -- RESET: Run information.
        self.error_message = None
        self.exception = None

        # access module var here to allow test mocking to work
        match = step_registry.registry.find_match(self)
        if match is None:
            runner.undefined.append(self)
            if not quiet:
                for formatter in runner.formatters:
                    formatter.match(NoMatch())

            self.status = 'undefined'
            if not quiet:
                for formatter in runner.formatters:
                    formatter.result(self)

            return False

        keep_going = True

        if not quiet:
            for formatter in runner.formatters:
                formatter.match(match)

        runner.run_hook('before_step', runner.context, self)
        runner.start_capture()

        try:
            start = time.time()
            # -- ENSURE:
            #  * runner.context.text/.table attributes are reset (#66).
            #  * Even EMPTY multiline text is available in context.
            runner.context.text = self.text
            runner.context.table = self.table
            match.run(runner.context)
            self.status = 'passed'
        except AssertionError, e:
            self.status = 'failed'
            self.exception = e
            if e.args:
                error = u'Assertion Failed: %s' % e
            else:
                # no assertion text; format the exception
                error = traceback.format_exc()
        except KeyboardInterrupt, e:
            runner.aborted = True
            error = u"ABORTED: By user (KeyboardInterrupt)."
            self.status = 'failed'
            self.exception = e
        except Exception, e:
            self.status = 'failed'
            error = traceback.format_exc()
            self.exception = e

        self.duration = time.time() - start

        runner.stop_capture()

        # flesh out the failure with details
        if self.status == 'failed':
            if capture:
                # -- CAPTURE-ONLY: Non-nested step failures.
                if runner.config.stdout_capture:
                    output = runner.stdout_capture.getvalue()
                    if output:
                        error += '\nCaptured stdout:\n' + output
                if runner.config.stderr_capture:
                    output = runner.stderr_capture.getvalue()
                    if output:
                        error += '\nCaptured stderr:\n' + output
                if runner.config.log_capture:
                    output = runner.log_capture.getvalue()
                    if output:
                        error += '\nCaptured logging:\n' + output
            self.error_message = error
            keep_going = False

        if not quiet:
            for formatter in runner.formatters:
                formatter.result(self)

        runner.run_hook('after_step', runner.context, self)
        return keep_going


class Table(Replayable):
    '''A `table`_ extracted from a *feature file*.

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
    '''
    type = "table"

    def __init__(self, headings, line=None, rows=[]):
        Replayable.__init__(self)
        self.headings = headings
        self.line = line
        self.rows = []
        for row in rows:
            self.add_row(row, line)

    def add_row(self, row, line=None):
        self.rows.append(Row(self.headings, row, line))

    def add_column(self, column_name, values=None, default_value=u""):
        """
        Adds a new column to this table.
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
        """
        Require that a column exists in the table.
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
        """
        Ensures that a column with the given name exists.
        If the column does not exist, the column is added.

        :param column_name: Name of column (as string).
        :return: Index of column (as number).
        """
        if self.has_column(column_name):
            return self.get_column_index(column_name)
        else:
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
        return not self == other

    def __iter__(self):
        return iter(self.rows)

    def __getitem__(self, index):
        return self.rows[index]

    def assert_equals(self, data):
        '''Assert that this table's cells are the same as the supplied "data".

        The data passed in must be a list of lists giving:

            [
                [row 1],
                [row 2],
                [row 3],
            ]

        If the cells do not match then a useful AssertionError will be raised.
        '''
        assert self == data
        raise NotImplementedError


class Row(object):
    '''One row of a `table`_ parsed from a *feature file*.

    Row data is accessible using a number of methods:

    **iteration**
      Iterating over the Row will yield the individual cells as strings.

    **named access**
      Individual cells may be accessed by heading name; row['name'] would give
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
    '''
    def __init__(self, headings, cells, line=None, comments=None):
        self.headings = headings
        self.comments = comments
        for c in cells:
            assert isinstance(c, unicode)
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
        return '<Row %r>' % (self.cells,)

    def __eq__(self, other):
        return self.cells == other.cells

    def __ne__(self, other):
        return not self == other

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
        """
        Converts the row and its cell data into a dictionary.
        :return: Row data as dictionary (without comments, line info).
        """
        from behave.compat.collections import OrderedDict
        return OrderedDict(self.items())


class Tag(unicode):
    '''Tags appear may be associated with Features or Scenarios.

    They're a subclass of regular strings (unicode pre-Python 3) with an
    additional ``line`` number attribute (where the tag was seen in the source
    feature file.

    See `controlling things with tags`_.
    '''
    def __new__(cls, name, line):
        o = unicode.__new__(cls, name)
        o.line = line
        return o


class Text(unicode):
    '''Store multiline text from a Step definition.

    The attributes are:

    .. attribute:: value

       The actual text parsed from the *feature file*.

    .. attribute:: content_type

       Currently only 'text/plain'.
    '''
    def __new__(cls, value, content_type=u'text/plain', line=0):
        assert isinstance(value, unicode)
        assert isinstance(content_type, unicode)
        o = unicode.__new__(cls, value)
        o.content_type = content_type
        o.line = line
        return o

    def line_range(self):
        line_count = len(self.splitlines())
        return (self.line, self.line + line_count + 1)

    def replace(self, old, new):
        return Text(super(Text, self).replace(old, new), self.content_type,
                    self.line)

    def assert_equals(self, expected):
        '''Assert that my text is identical to the "expected" text.

        A nice context diff will be displayed if they do not match.'
        '''
        if self == expected:
            return True
        diff = []
        for line in difflib.unified_diff(self.splitlines(),
                                         expected.splitlines()):
            diff.append(line)
        # strip unnecessary diff prefix
        diff = ['Text does not match:'] + diff[3:]
        raise AssertionError('\n'.join(diff))


class Match(Replayable):
    '''An parameter-matched *feature file* step name extracted using
    step decorator `parameters`_.

    .. attribute:: func

       The step function that this match will be applied to.

    .. attribute:: arguments

       A list of :class:`behave.model.Argument` instances containing the
       matched parameters from the step name.
    '''
    type = "match"

    def __init__(self, func, arguments=None):
        super(Match, self).__init__()
        self.func = func
        self.arguments = arguments
        self.location = None
        if func:
            self.location = self.make_location(func)

    def __repr__(self):
        if self.func:
            func_name = self.func.__name__
        else:
            func_name = '<no function>'
        return '<Match %s, %s>' % (func_name, self.location)

    def __eq__(self, other):
        if not isinstance(other, Match):
            return False
        return (self.func, self.location) == (other.func, other.location)

    def with_arguments(self, arguments):
        match = copy.copy(self)
        match.arguments = arguments
        return match

    def run(self, context):
        args = []
        kwargs = {}
        for arg in self.arguments:
            if arg.name is not None:
                kwargs[arg.name] = arg.value
            else:
                args.append(arg.value)

        with context.user_mode():
            self.func(context, *args, **kwargs)

    @staticmethod
    def make_location(step_function):
        '''
        Extracts the location information from the step function and builds
        the location string (schema: "{source_filename}:{line_number}").

        :param step_function: Function whose location should be determined.
        :return: Step function location as string.
        '''
        filename = relpath(step_function.func_code.co_filename, os.getcwd())
        line_number = step_function.func_code.co_firstlineno
        return FileLocation(filename, line_number)


class NoMatch(Match):
    '''
    Used for an "undefined step" when it can not be matched with a
    step definition.
    '''

    def __init__(self):
        Match.__init__(self, func=None)
        self.func = None
        self.arguments = []
        self.location = None
