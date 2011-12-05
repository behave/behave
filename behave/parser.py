from __future__ import with_statement

from behave import model, i18n

DEFAULT_LANGUAGE = 'en'


def parse_file(filename, language=None):
    with open(filename, 'rb') as f:
        # file encoding is assumed to be utf8. Oh, yes.
        data = f.read().decode('utf8')
    return parse_feature(data, language, filename)


def parse_feature(data, language=None, filename=None):
    # ALL data operated on by the parser MUST be unicode
    assert isinstance(data, unicode)

    try:
        result = Parser(language).parse(data, filename)
    except ParserError, e:
        e.filename = filename
        raise

    return result


class ParserError(Exception):
    def __init__(self, message, line, filename=None):
        if line:
            message += ' at line %d' % line
        super(ParserError, self).__init__(message)
        self.line = line
        self.filename = filename

    def __str__(self):
        if self.filename:
            return 'Failed to parse "%s": %s' % (self.filename, self.args[0])
        return 'Failed to parse <string>: %s' % self.args[0]


class Parser(object):
    def __init__(self, language=None):
        self.language = language
        self.reset()

    def reset(self):
        # This can probably go away.
        if self.language:
            self.keywords = i18n.languages[self.language]
        else:
            self.keywords = None

        self.state = 'init'
        self.line = 0
        self.last_step = None
        self.multiline_start = None
        self.multiline_leading = None
        self.multiline_terminator = None

        self.filename = None
        self.feature = None
        self.statement = None
        self.tags = []
        self.lines = []
        self.table = None
        self.examples = None

    def parse(self, data, filename=None):
        self.reset()

        self.filename = filename

        for line in data.split('\n'):
            self.line += 1
            if not line.strip():
                continue
            self.action(line)

        if self.table:
            self.action_table('')

        feature = self.feature
        feature.parser = self
        self.reset()
        return feature

    def action(self, line):
        if line.strip().startswith('#'):
            if self.keywords or self.state != 'init' or self.tags:
                return

            line = line.strip()[1:].strip()
            if line.lstrip().lower().startswith('language:'):
                language = line[9:].strip()
                self.language = language
                self.keywords = i18n.languages[language]
            return

        func = getattr(self, 'action_' + self.state, None)
        if func is None:
            raise ParserError('Parser in unknown state ' + self.state,
                              self.line)
        if not func(line):
            raise ParserError("Parser failure in state " + self.state,
                              self.line)

    def action_init(self, line):
        line = line.strip()

        if line.startswith('@'):
            self.tags.extend([model.Tag(tag.strip(), self.line)
                for tag in line[1:].split('@')])
            return True
        feature_kwd = self.match_keyword('feature', line)
        if feature_kwd:
            name = line[len(feature_kwd) + 1:].strip()
            self.feature = model.Feature(self.filename, self.line, feature_kwd,
                                         name, tags=self.tags)
            self.tags = []
            self.state = 'feature'
            return True
        return False

    def action_feature(self, line):
        line = line.strip()

        if line.startswith('@'):
            self.tags.extend([model.Tag(tag.strip(), self.line)
                for tag in line[1:].split('@')])
            return True

        background_kwd = self.match_keyword('background', line)
        if background_kwd:
            name = line[len(background_kwd) + 1:].strip()
            self.statement = model.Background(self.filename, self.line,
                                              background_kwd, name)
            self.feature.background = self.statement
            self.state = 'steps'
            return True

        scenario_kwd = self.match_keyword('scenario', line)
        if scenario_kwd:
            name = line[len(scenario_kwd) + 1:].strip()
            self.statement = model.Scenario(self.filename, self.line,
                                            scenario_kwd, name, tags=self.tags)
            self.tags = []
            self.feature.add_scenario(self.statement)
            self.state = 'steps'
            return True

        scenario_outline_kwd = self.match_keyword('scenario_outline', line)
        if scenario_outline_kwd:
            name = line[len(scenario_outline_kwd) + 1:].strip()
            self.statement = model.ScenarioOutline(self.filename, self.line,
                                                   scenario_outline_kwd, name,
                                                   tags=self.tags)
            self.tags = []
            self.feature.add_scenario(self.statement)
            self.state = 'steps'
            return True

        self.feature.description.append(line)
        return True

    def action_steps(self, line):
        stripped = line.lstrip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            self.state = 'multiline'
            self.multiline_start = self.line
            self.multiline_terminator = stripped[:3]
            self.multiline_leading = line.index(stripped[0])
            return True

        line = line.strip()

        step = self.parse_step(line)
        if step:
            self.statement.steps.append(step)
            return True

        if line.startswith('@'):
            self.tags.extend([model.Tag(tag.strip(), self.line)
                for tag in line[1:].split('@')])
            return True

        scenario_kwd = self.match_keyword('scenario', line)
        if scenario_kwd:
            name = line[len(scenario_kwd) + 1:].strip()
            self.statement = model.Scenario(self.filename, self.line,
                                            scenario_kwd, name, tags=self.tags)
            self.tags = []
            self.feature.add_scenario(self.statement)
            return True

        scenario_outline_kwd = self.match_keyword('scenario_outline', line)
        if scenario_outline_kwd:
            name = line[len(scenario_outline_kwd) + 1:].strip()
            self.statement = model.ScenarioOutline(self.filename, self.line,
                                                   scenario_outline_kwd, name,
                                                   tags=self.tags)
            self.tags = []
            self.feature.add_scenario(self.statement)
            self.state = 'steps'
            return True

        examples_kwd = self.match_keyword('examples', line)
        if examples_kwd:
            if not isinstance(self.statement, model.ScenarioOutline):
                message = 'Examples must only appear inside scenario outline'
                raise ParserError(message, self.line)
            name = line[len(examples_kwd) + 1:].strip()
            self.examples = model.Examples(self.filename, self.line,
                                           examples_kwd, name)
            self.statement.examples.append(self.examples)
            self.state = 'table'
            return True

        if line.startswith('|'):
            self.state = 'table'
            return self.action_table(line)

        return False

    def action_multiline(self, line):
        if line.strip().startswith(self.multiline_terminator):
            step = self.statement.steps[-1]
            step.text = model.Text(u'\n'.join(self.lines), u'text/plain',
                self.multiline_start)
            if step.name.endswith(':'):
                step.name = step.name[:-1]
            self.lines = []
            self.multiline_terminator = None
            self.state = 'steps'
            return True

        self.lines.append(line[self.multiline_leading:])
        return True

    def action_table(self, line):
        line = line.strip()

        if not line.startswith('|'):
            if self.examples:
                self.examples.table = self.table
                self.examples = None
            else:
                step = self.statement.steps[-1]
                step.table = self.table
                if step.name.endswith(':'):
                    step.name = step.name[:-1]
            self.table = None
            self.state = 'steps'
            return self.action_steps(line)

        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        if self.table is None:
            self.table = model.Table(cells, self.line)
        else:
            if len(cells) != len(self.table.headings):
                raise ParserError("Malformed table", self.line)
            self.table.add_row(cells, self.line)
        return True

    def match_keyword(self, keyword, line):
        if not self.keywords:
            self.language = DEFAULT_LANGUAGE
            self.keywords = i18n.languages[DEFAULT_LANGUAGE]
        for alias in self.keywords[keyword]:
            if line.startswith(alias + ':'):
                return alias
        return False

    def parse_step(self, line):
        for step_type in ('given', 'when', 'then', 'and', 'but'):
            for kw in self.keywords[step_type]:
                if kw.endswith('<'):
                    whitespace = ''
                    kw = kw[:-1]
                else:
                    whitespace = ' '

                # try to match the keyword; also attempt a purely lowercase
                # match if that'll work
                if not (line.startswith(kw + whitespace)
                        or line.lower().startswith(kw.lower() + whitespace)):
                    continue

                name = line[len(kw):].strip()
                if step_type in ('and', 'but'):
                    if not self.last_step:
                        raise ParserError("No previous step", self.line)
                    step_type = self.last_step
                else:
                    self.last_step = step_type
                step = model.Step(self.filename, self.line, kw, step_type,
                                  name)
                return step
        return None
