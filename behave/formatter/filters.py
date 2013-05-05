# -*- coding: utf-8 -*-
# FIXME:
__status__ = "DEAD, BROKEN"

from gherkin.tag_expression import TagExpression


class LineFilter(object):
    def __init__(self, lines):
        self.lines = lines

    def eval(self, tags, names, ranges):
        for r in ranges:
            for line in self.lines:
                if r[0] <= line <= r[1]:
                    return True
        return False

    def filter_table_body_rows(self, rows):
        body = [r for r in rows[1:] if r.line in self.lines]
        return [rows[0]] + body


class RegexpFilter(object):
    def __init__(self, regexen):
        self.regexen = regexen

    def eval(self, tags, names, ranges):
        for regex in self.regexen:
            for name in names:
                if regex.search(name):
                    return True
        return False

    def filter_table_body_rows(self, rows):
        return rows


class TagFilter(object):
    def __init__(self, tags):
        self.tag_expression = TagExpression(tags)

    def eval(self, tags, names, ranges):
        return self.tag_expression.eval([tag.name for tag in set(tags)])

    def filter_table_body_rows(self, rows):
        return rows
