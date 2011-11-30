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
                if scenario.status != 'skipped':
                    skipped = False
            else:
                for scenario in scenario_or_outline:
                    if scenario.status == 'failed':
                        return 'failed'
                    if scenario.status != 'skipped':
                        skipped = False
        return skipped and 'skipped' or 'passed'


class Background(BasicStatement, Replayable):
    type = "background"

    def __init__(self, filename, line, keyword, name, steps=[]):
        super(Background, self).__init__(filename, line, keyword, name)
        self.steps = steps or []

    def __repr__(self):
        return '<Background "%s">' % self.name

    def __iter__(self):
        return iter(self.steps)


class Scenario(TagStatement, Replayable):
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
        return 'passed'


class ScenarioOutline(Scenario):
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
    type = "examples"

    def __init__(self, filename, line, keyword, name, table=None):
        super(Examples, self).__init__(filename, line, keyword, name)
        self.table = table


class Step(BasicStatement, Replayable):
    type = "step"

    def __init__(self, filename, line, keyword, step_type, name, string=None,
                 table=None):
        super(Step, self).__init__(filename, line, keyword, name)
        self.step_type = step_type
        self.string = string
        self.table = table

        self.status = None
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
    def __new__(cls, name, line):
        o = unicode.__new__(cls, name)
        o.line = line
        return o

'''
    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
'''

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
