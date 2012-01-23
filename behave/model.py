from __future__ import with_statement

import copy
import difflib
import itertools
import os.path
import time
import traceback

from behave import step_registry


def relpath(path, other):
    # Python 2.5 doesn't know about relpath
    if hasattr(os.path, 'relpath'):
        return os.path.relpath(path, other)
    return path


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


class BasicStatement(object):
    def __init__(self, filename, line, keyword, name):
        self.filename = filename or '<string>'
        self.line = line
        assert isinstance(keyword, unicode)
        assert isinstance(name, unicode)
        self.keyword = keyword
        self.name = name

    def __cmp__(self, other):
        return cmp((self.keyword, self.name), (other.keyword, other.name))

    @property
    def location(self):
        p = relpath(self.filename, os.getcwd())
        return '%s:%d' % (p, self.line)

    def to_dict(self):
        return dict((k, v) for k, v in self.__dict__.items() if k[0] != '_')


class TagStatement(BasicStatement):
    def __init__(self, filename, line, keyword, name, tags):
        super(TagStatement, self).__init__(filename, line, keyword, name)
        self.tags = tags


class Replayable(object):
    type = None

    def replay(self, formatter):
        getattr(formatter, self.type)(self)


class Feature(TagStatement, Replayable):
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

       The file name (or "<string>") of the *feature file* where the feature was
       found.

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

    def __repr__(self):
        return '<Feature "%s": %d scenario(s)>' % \
            (self.name, len(self.scenarios))

    def __iter__(self):
        return iter(self.scenarios)

    def add_scenario(self, scenario):
        scenario.feature = self
        scenario.background = self.background
        self.scenarios.append(scenario)

    @property
    def status(self):
        skipped = True
        for scenario_or_outline in self.scenarios:
            if isinstance(scenario_or_outline, Scenario):
                scenario = scenario_or_outline
                if scenario.status == 'failed':
                    return 'failed'
                if scenario.status == 'untested':
                    return 'untested'
                if scenario.status != 'skipped':
                    skipped = False
            else:
                for scenario in scenario_or_outline:
                    if scenario.status == 'failed':
                        return 'failed'
                    if scenario.status == 'untested':
                        return 'untested'
                    if scenario.status != 'skipped':
                        skipped = False
        return skipped and 'skipped' or 'passed'

    @property
    def duration(self):
        if self.background:
            duration = self.background.duration or 0.0
        else:
            duration = 0.0
        for scenario in self.scenarios:
            duration += scenario.duration
        return duration

    def run(self, runner):
        failed = False

        runner.context._push()
        runner.context.feature = self

        # run this feature if the tags say to for itself or any one of its
        # scenarios
        run_feature = runner.config.tags.check(self.tags)
        for scenario in self:
            run_feature = run_feature or runner.config.tags.check(scenario.tags)

        if run_feature or runner.config.show_skipped:
            runner.formatter.feature(self)

        # current tags as a set
        runner.context.tags = set(self.tags)

        if run_feature:
            for tag in self.tags:
                runner.run_hook('before_tag', runner.context, tag)
            runner.run_hook('before_feature', runner.context, self)

        if self.background and (run_feature or runner.config.show_skipped):
            runner.formatter.background(self.background)

        for scenario in self:
            failed = scenario.run(runner)

            # do we want to stop on the first failure?
            if failed and runner.config.stop:
                break

        if run_feature:
            runner.run_hook('after_feature', runner.context, self)
            for tag in self.tags:
                runner.run_hook('after_tag', runner.context, tag)

        runner.context._pop()

        runner.formatter.eof()
        if run_feature or runner.config.show_skipped:
            runner.formatter.stream.write('\n')

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

       The time, in seconds, that it took to run this background. If read before
       the background is run it will return 0.0.

    .. attribute:: filename

       The file name (or "<string>") of the *feature file* where the scenario was
       found.

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


class Scenario(TagStatement, Replayable):
    '''A `scenario`_ parsed from a *feature file*.

    The attributes are:

    .. attribute:: keyword

       This is the keyword as seen in the *feature file*. In English this will
       typically be "Scenario".

    .. attribute:: name

       The name of the scenario (the text after "Scenario:".)

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

       The file name (or "<string>") of the *feature file* where the scenario was
       found.

    .. attribute:: line

       The line number of the *feature file* where the scenario was found.

    .. _`scenario`: gherkin.html#scenarios
    '''
    type = "scenario"

    def __init__(self, filename, line, keyword, name, tags=[], steps=[]):
        super(Scenario, self).__init__(filename, line, keyword, name, tags)
        self.steps = steps or []

        self.background = None

    def __repr__(self):
        return '<Scenario "%s">' % self.name

    def __iter__(self):
        if self.background is not None:
            return itertools.chain(self.background, self.steps)
        else:
            return iter(self.steps)

    @property
    def status(self):
        for step in self.steps:
            if step.status == 'failed':
                return 'failed'
            if step.status == 'skipped':
                return 'skipped'
            if step.status == 'untested':
                return 'untested'
        return 'passed'

    @property
    def duration(self):
        duration = 0
        for step in self.steps:
            duration += step.duration
        return duration

    def run(self, runner):
        failed = False

        tags = runner.feature.tags + self.tags
        run_scenario = runner.config.tags.check(tags)
        run_steps = run_scenario and not runner.config.dry_run

        if run_scenario or runner.config.show_skipped:
            runner.formatter.scenario(self)

        runner.context._push()
        runner.context.scenario = self

        # current tags as a set
        runner.context.tags = set(tags)

        if run_scenario:
            for tag in self.tags:
                runner.run_hook('before_tag', runner.context, tag)
            runner.run_hook('before_scenario', runner.context, self)

        runner.setup_capture()

        if run_scenario or runner.config.show_skipped:
            for step in self:
                runner.formatter.step(step)

        for step in self:
            if run_steps:
                if not step.run(runner):
                    run_steps = False
                    failed = True
                    runner.context._set_root_attribute('failed', True)
            else:
                step.status = 'skipped'
                if self.status is None:
                    self.status = 'skipped'

        runner.teardown_capture()

        if run_scenario:
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

       The time, in seconds, that it took to test the scenarios of this outline.
       If read before the scenarios are tested it will return 0.0.

    .. attribute:: filename

       The file name (or "<string>") of the *feature file* where the scenario was
       found.

    .. attribute:: line

       The line number of the *feature file* where the scenario was found.

    .. _`scenario outline`: gherkin.html#scenario-outlines
    '''
    type = "scenario_outline"

    def __init__(self, filename, line, keyword, name, tags=[], steps=[],
                 examples=[]):
        super(ScenarioOutline, self).__init__(filename, line, keyword, name,
                                              tags, steps)
        self.examples = examples or []
        self._scenarios = []

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

    @property
    def status(self):
        for scenario in self.scenarios:
            if scenario.status == 'failed':
                return 'failed'
            if scenario.status == 'skipped':
                return 'skipped'
            if scenario.status == 'untested':
                return 'untested'
        return 'passed'

    @property
    def duration(self):
        duration = 0
        for scenario in self.scenarios:
            duration += scenario.duration
        return duration

    def run(self, runner):
        failed = False

        for sub in self.scenarios:
            runner.context._set_root_attribute('active_outline', sub._row)
            failed = sub.run(runner)
            if failed and runner.config.stop:
                return False
        runner.context._set_root_attribute('active_outline', None)

        return failed


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

       The file name (or "<string>") of the *feature file* where the scenario was
       found.

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

       If the step failed then this will hold any error information, as a single
       string. It will otherwise be None.

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

    def __repr__(self):
        return '<%s "%s">' % (self.step_type, self.name)

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

    def run(self, runner, quiet=False):
        # access module var here to allow test mocking to work
        match = step_registry.registry.find_match(self)
        if match is None:
            runner.undefined.append(self)
            if not quiet:
                runner.formatter.match(NoMatch())
            self.status = 'undefined'
            if not quiet:
                runner.formatter.result(self)
            return False

        keep_going = True

        if not quiet:
            runner.formatter.match(match)
        runner.run_hook('before_step', runner.context, self)
        runner.start_capture()

        try:
            start = time.time()
            if self.text:
                runner.context.text = self.text
            if self.table:
                runner.context.table = self.table
            match.run(runner.context)
            self.status = 'passed'
        except AssertionError, e:
            self.status = 'failed'
            if e.args:
                error = u'Assertion Failed: %s' % (str(e),)
            else:
                # no assertion text; format the exception
                error = traceback.format_exc()
        except Exception, e:
            self.status = 'failed'
            error = traceback.format_exc()
            self.exception = e

        self.duration = time.time() - start

        runner.stop_capture()

        # flesh out the failure with details
        if self.status == 'failed':
            if runner.config.stdout_capture:
                output = runner.stdout_capture.getvalue()
                if output:
                    error += '\nCaptured stdout:\n' + output
            if runner.config.log_capture:
                output = runner.log_capture.getvalue()
                if output:
                    error += '\nCaptured logging:\n' + output
            self.error_message = error
            keep_going = False

        if not quiet:
            runner.formatter.result(self)
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
      table[0] gives the first non-heading row and table[-1] gives the last row.

    The attributes are:

    .. attribute:: headings

       The headings of the table as a list of strings.

    .. attribute:: rows

       An list of instances of :class:`~behave.model.Row` that make up the body
       of the table in the *feature file*.

    Tables are also comparable, for what that's worth. Headings and row data are
    compared.

    .. _`table`: gherkin.html#table
    '''
    type = "table"

    def __init__(self, headings, line, rows=[]):
        self.headings = headings
        self.line = line
        self.rows = []
        for row in rows:
            self.add_row(row, line)

    def add_row(self, row, line):
        self.rows.append(Row(self.headings, None, row, line))

    def __repr__(self):
        return "<Table: %dx%d>" % (len(self.headings), len(self.rows))

    def __eq__(self, other):
        if self.headings != other.headings:
            return False
        for my_row, their_row in zip(self.rows, other.rows):
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
    def __init__(self, headings, comments, cells, line):
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

    def __iter__(self):
        return iter(self.cells)

    def items(self):
        return zip(self.headings, self.cells)


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
        return Text(super(Text, self).replace(old, new), self.content_type, self.line)

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

       A list of :class:`behave.model.Argument` instances containing the matched
       parameters from the step name.
    '''
    type = "match"

    def __init__(self, func, arguments=None):
        self.func = func
        self.arguments = arguments

        filename = relpath(func.func_code.co_filename, os.getcwd())
        self.location = '%s:%d' % (filename, func.func_code.co_firstlineno)

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


class NoMatch(Match):
    def __init__(self):
        self.func = None
        self.arguments = []
        self.location = None
