#-*- coding: utf8 -*-

# This file originates from Freshen: http://github.com/rlisagor/freshen
# It is distributed under the terms of the GNU GPL Version 3 or later.

# This line ensures that frames from this file will not be shown in tracebacks
__unittest = 1

from pyparsing import *
import copy
import logging
import os
import re
import textwrap

try:
    from os.path import relpath
except Exception, e:
    from freshen.compat import relpath

log = logging.getLogger('freshen')

class Feature(object):

    def __init__(self, use_step_defs, tags, keyword, name, description,
                 background, scenarios):
        self.use_step_defs = use_step_defs
        self.tags = tags
        self.keyword = keyword
        self.name = name
        self.description = '\n'.join(description)
        self.scenarios = scenarios
        self.background = None

        if background != []:
            self.background = background[0]

        for sc in scenarios:
            sc.feature = self
            sc.background = self.background

    def __repr__(self):
        return '<Feature "%s": %d scenario(s)>' % (self.name, len(self.scenarios))

    def has_background(self):
        return self.background is not None

    def iter_scenarios(self):
        for sco in self.scenarios:
            yield sco


class Background(object):

    def __init__(self, keyword, name, steps):
        self.keyword = keyword
        self.name = name
        self.steps = steps

    def __repr__(self):
        return '<Background "%s">' % self.name

    def iter_steps(self):
        for step in self.steps:
            yield step

class Scenario(object):

    def __init__(self, tags, keyword, name, steps):
        self.tags = tags
        self.keyword = keyword
        self.name = name
        self.steps = steps
        self.background = None

    def __repr__(self):
        return '<Scenario "%s">' % self.name

    def get_tags(self):
        return self.tags + self.feature.tags

    def iterate(self):
        yield self

    def iter_steps(self):
        if self.background is not None:
            for step in self.background.iter_steps():
                yield step

        for step in self.steps:
            yield step


class ScenarioOutline(Scenario):

    def __init__(self, tags, keyword, name, steps, examples):
        self.examples = examples
        super(ScenarioOutline, self).__init__(tags, keyword, name, steps)

    def __repr__(self):
        return '<ScenarioOutline "%s">' % self.name

    def iterate(self):
        for ex in self.examples:
            for values in ex.table.iterrows():
                new_steps = []
                for step in self.steps:
                    new_steps.append(step.set_values(values))
                sc = Scenario(self.tags, self.name, new_steps)
                sc.feature = self.feature
                sc.background = self.background
                yield sc


class Step(object):

    def __init__(self, step_type, name, arg=None):
        self.keyword, self.step_type = step_type
        self.name = name
        if isinstance(arg, Table):
            self.table = arg
            self.string = None
        else:
            self.table = None
            self.string = arg

    def __repr__(self):
        return '<%s "%s">' % (self.step_type, self.name)

    def source_location(self, absolute=True):
        p = relpath(self.src_file, os.getcwd()) if absolute else self.src_file
        return '%s:%d' % (p, self.src_line)

    def set_values(self, value_dict):
        result = copy.deepcopy(self)
        for name, value in value_dict.iteritems():
            result.match = result.match.replace("<%s>" % name, value)
        return result


class Examples(object):

    def __init__(self, keyword, name, table):
        self.keyword = keyword
        self.name = name
        self.table = table


class Table(object):

    def __init__(self, headings, rows):
        assert [len(r) == len(headings) for r in rows], "Malformed table"

        self.headings = headings
        self.rows = rows

    def __repr__(self):
        return "<Table: %dx%d>" % (len(self.headings), len(self.rows))

    def iterrows(self):
        for row in self.rows:
            yield dict(zip(self.headings, row))


def grammar(fname, l, convert=True, base_line=0):
    # l = language

    def create_object(klass):
        def untokenize(s, loc, toks):
            result = []
            for t in toks:
                if isinstance(t, ParseResults):
                    t = t.asList()
                result.append(t)
            obj = klass(*result)
            obj.src_file = fname
            obj.src_line = base_line + lineno(loc, s)
            return obj
        return untokenize

    def process_descr(s):
        return [p.strip() for p in s[0].strip().split("\n")]

    # This has to be an array for compatibility with Python versions which do not have "nonlocal"
    last_step_type = [None]

    def process_given_step(s):
        last_step_type[0] = 'given'
        return (s[0], 'given')

    def process_when_step(s):
        last_step_type[0] = 'when'
        return (s[0], 'when')

    def process_then_step(s):
        last_step_type[0] = 'then'
        return (s[0], 'then')

    def process_and_but_step(orig, loc, s):
        if last_step_type[0] == None:
            raise ParseFatalException(orig, loc,
                        "'And' or 'But' steps can only come after 'Given', 'When', or 'Then'")
        return (s[0], last_step_type[0])

    def process_string(s):
        return s[0].strip()

    def process_m_string(s):
        return textwrap.dedent(s[0])

    def process_tag(s):
        return s[0].strip("@")

    def or_words(words, kind, suffix='', parse_acts=None):
        elements = []
        for index, native_word in enumerate(words):
            for word in l.words(native_word):
                element = kind(word + suffix)
                if parse_acts is not None:
                    element.setParseAction(parse_acts[index])
                elements.append(element)
        return Or(elements)

    empty_not_n    = empty.copy().setWhitespaceChars(" \t")
    tags           = OneOrMore(Word("@", alphanums + "_").setParseAction(process_tag))

    step_file      = quotedString.setParseAction( removeQuotes )
    list_of_step_files = step_file + ZeroOrMore(Suppress(',') + step_file)
    use_step_defs  = or_words(['use_step_defs'], Suppress, ':') + list_of_step_files

    following_text = empty_not_n + restOfLine + Suppress(lineEnd)
    section_header = lambda name: Literal(name) + Suppress(":") + following_text

    section_name   = or_words(['scenario', 'scenario_outline', 'background'], Literal)
    descr_block    = Group(SkipTo(section_name | tags).setParseAction(process_descr))

    table_row      = Group(Suppress("|") +
                           delimitedList(
                                         CharsNotIn("|\n").setParseAction(process_string) +
                                         Suppress(empty_not_n), delim="|") +
                           Suppress("|"))
    table          = table_row + Group(OneOrMore(table_row))

    m_string       = (Suppress(Literal('"""') + lineEnd).setWhitespaceChars(" \t") +
                      SkipTo((lineEnd +
                              Literal('"""')).setWhitespaceChars(" \t")).setWhitespaceChars("") +
                      Suppress('"""'))
    m_string.setParseAction(process_m_string)

    step_name      = or_words(['given', 'when', 'then', 'and', 'but'], Keyword,
                              parse_acts=[process_given_step, process_when_step, process_then_step,
                                          process_and_but_step, process_and_but_step])
    step           = step_name + following_text + Optional(table | m_string)
    steps          = Group(ZeroOrMore(step))

    example        = or_words(['examples'], section_header) + table

    background     = or_words(['background'], section_header) + steps

    scenario       = Group(Optional(tags)) + or_words(['scenario'], section_header) + steps
    scenario_outline = Group(Optional(tags)) + or_words(['scenario_outline'], section_header) + steps + Group(OneOrMore(example))

    feature        = (Group(Optional(use_step_defs)) +
                      Group(Optional(tags)) +
                      or_words(['feature'], section_header) +
                      descr_block +
                      Group(Optional(background)) +
                      Group(OneOrMore(scenario | scenario_outline)))

    # Ignore tags for now as they are not supported
    feature.ignore(pythonStyleComment)
    steps.ignore(pythonStyleComment)

    if convert:
        table.setParseAction(create_object(Table))
        step.setParseAction(create_object(Step))
        background.setParseAction(create_object(Background))
        scenario.setParseAction(create_object(Scenario))
        scenario_outline.setParseAction(create_object(ScenarioOutline))
        example.setParseAction(create_object(Examples))
        feature.setParseAction(create_object(Feature))

    return feature, steps

def parse_file(fname, language, convert=True):
    feature, _ = grammar(fname, language, convert)
    try:
        file_obj = open(fname)
        if convert:
            feat = feature.parseFile(file_obj)[0]
        else:
            feat = feature.parseFile(file_obj)
    finally:
        file_obj.close()
    return feat

def parse_steps(spec, fname, base_line, language, convert=True):
    _, steps = grammar(fname, language, convert, base_line)
    if convert:
        return steps.parseString(spec)[0]
    else:
        return steps.parseString(spec)

