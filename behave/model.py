import collections
import copy
import itertools
import os.path


def relpath(path, other):
    # Python 2.5 doesn't know about relpath
    if hasattr(os.path, 'relpath'):
        return os.path.relpath(path, other)
    return path


class Argument(object):
    '''An argument found in a *feature file* step name and extracted using
    step decorator `parameters`_.

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

    def to_dict(self):
        return dict((k, v) for k, v in self.__dict__.items() if k[0] != '_')

    @property
    def location(self):
        p = relpath(self.filename, os.getcwd())
        return '%s:%d' % (p, self.line)


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

       A list of @tags (as :class:`~behave.model.Tag`) attached to the
       feature. See `controlling things with tags`_.

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


class Background(BasicStatement, Replayable):
    '''A `background`_ parsed from a *feature file*.

    .. attribute:: keyword

       This is the keyword as seen in the *feature file*. In English this will
       typically be "Background".

    .. attribute:: name

       The name of the background (the text after "Background:".)

    .. attribute:: steps

       A list of :class:`~behave.model.Step` making up this background.

    .. attribute:: filename

       The file name (or "<string>") of the *feature file* where the scenario was
       found.

    .. attribute:: line

       The line number of the *feature file* where the scenario was found.

    .. _`background`: gherkin.html#scenarios
    '''
    type = "background"

    def __init__(self, filename, line, keyword, name, steps=[]):
        super(Background, self).__init__(filename, line, keyword, name)
        self.steps = steps or []

    def __repr__(self):
        return '<Background "%s">' % self.name

    def __iter__(self):
        return iter(self.steps)


class Scenario(TagStatement, Replayable):
    '''A `scenario`_ parsed from a *feature file*.

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

       A list of @tags (as :class:`~behave.model.Tag`) attached to the
       scenario. See `controlling things with tags`_.

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


class ScenarioOutline(Scenario):
    '''A `scenario outline`_ parsed from a *feature file*.

    A scenario outline extends the existing :class:`~behave.model.Scenario`
    class with the addition of the :class:`~behave.model.Examples` tables of
    data from the *feature file*.

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

       A list of @tags (as :class:`~behave.model.Tag`) attached to the
       scenario. See `controlling things with tags`_.

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

        self.scenarios = []
        for example in self.examples:
            for values in example.table.iterrows():
                new_steps = []
                for step in self.steps:
                    new_steps.append(step.set_values(values))
                scenario = Scenario(self.tags, self.name, new_steps)
                scenario.feature = self.feature
                scenario.background = self.background
                self.scenarios.append(scenario)

    def __repr__(self):
        return '<ScenarioOutline "%s">' % self.name

    def __iter__(self):
        return iter(self.scenarios)


class Examples(BasicStatement, Replayable):
    '''A table parsed from a `scenario outline`_ in a *feature file*.

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

    .. attribute:: keyword

       This is the keyword as seen in the *feature file*. In English this will
       typically be "Given", "When", "Then" or a number of other words.

    .. attribute:: name

       The name of the step (the text after "Given" etc.)

    .. attribute:: step_type

       The type of step as determined by the keyword. If the keyword is "and"
       then the previous keyword in the *feature file* will determine this
       step's step_type.

    .. attribute:: table

       An instance  of :class:`~behave.model.Table` that came with the step
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

    def __init__(self, filename, line, keyword, step_type, name, string=None,
                 table=None):
        super(Step, self).__init__(filename, line, keyword, name)
        self.step_type = step_type
        self.string = string        # unused?
        self.table = table

        self.status = 'untested'
        self.duration = 0.0
        self.error_message = None

    def __repr__(self):
        return '<%s "%s">' % (self.step_type, self.name)

    def set_values(self, value_dict):
        result = copy.deepcopy(self)
        for name, value in value_dict.iteritems():
            result.match = result.match.replace("<%s>" % name, value)
        return result


class Table(Replayable):
    type = "table"

    def __init__(self, headings, rows=[]):
        self.headings = headings
        self.rows = rows or []

    def __repr__(self):
        return "<Table: %dx%d>" % (len(self.headings), len(self.rows))

    def __eq__(self, other):
        if self.headings != other.headings:
            return False
        for my_row, their_row in zip(self.rows, other.rows):
            if my_row != their_row:
                return False
        return True

    def __iter__(self):
        Row = collections.namedtuple('Row', self.headings)
        return iter([Row(*row) for row in self.rows])


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


class DocString(object):
    def __init__(self, content_type, value, line):
        assert isinstance(content_type, unicode)
        assert isinstance(value, unicode)
        self.content_type = content_type
        self.value = value
        self.line = line

    def line_range(self):
        line_count = len(self.value.splitlines())
        return (self.line, self.line + line_count + 1)


class Row(object):
    def __init__(self, comments, cells, line):
        self.comments = comments
        for c in cells:
            assert isinstance(c, unicode)
        self.cells = cells
        self.line = line


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
        return '<Match %s, %s>' % (self.func.__name__, self.location)

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

        self.func(context, *args, **kwargs)


class NoMatch(Match):
    def __init__(self):
        self.func = None
        self.arguments = []
        self.location = None


class Result(Replayable):
    type = "result"

    def __init__(self, status, duration, error_message):
        assert isinstance(status, unicode)
        self.status = status
        self.duration = duration
        self.error_message = error_message
