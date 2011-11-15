def ensure_unicode(value):
    if value is None:
        return None
    if type(value) is not unicode:
        value = value.decode('utf8')
    return value

class Argument(object):
    def __init__(self, offset, val):
        self.offset = offset
        self.val = ensure_unicode(val)

class Dictable(object):
    include_type = False
    
    def to_dict(self):
        result = {}
        if self.include_type:
            result['type'] = self.type
        for name, value in self.__dict__.items():
            if isinstance(value, BasicStatement):
                value = value.to_dict()
            if type(value) is list:
                new_value = []
                for element in value:
                    if isinstance(element, BasicStatement):
                        new_value.append(element.to_dict())
                    else:
                        new_value.append(element)
                value = new_value
            if value not in ([], None):
                result[name] = value
        return result
    
class BasicStatement(Dictable):
    def __init__(self, comments, keyword, name, line):
        self.comments = comments
        self.keyword = ensure_unicode(keyword)
        self.name = ensure_unicode(name)
        self.line = line

    def line_range(self):
        if self.comments:
            first = self.comments[0].line
        else:
            first = self.first_non_comment_line()
        return first, self.line

    def first_non_comment_line(self):
        return self.line
    
class DescribedStatement(BasicStatement):
    def __init__(self, comments, keyword, name, description, line):
        super(DescribedStatement, self).__init__(comments, keyword, name, line)
        self.description = ensure_unicode(description)

class TagStatement(DescribedStatement):
    def __init__(self, comments, tags, keyword, name, description, line):
        super(TagStatement, self).__init__(comments, keyword, name, description,
                                           line)
        self.tags = tags

    def first_non_comment_line(self):
        if self.tags:
            return self.tags[0].line
        return self.line

class Replayable(object):
    type = None

    def replay(self, formatter):
        getattr(formatter, self.type)(self)

class Feature(TagStatement, Replayable):
    type = "feature"

class Background(DescribedStatement, Replayable):
    type = "background"
    include_type = True

class Scenario(TagStatement, Replayable):
    type = "scenario"
    include_type = True

class ScenarioOutline(TagStatement, Replayable):
    type = "scenario_outline"
    include_type = True

class Examples(TagStatement, Replayable):
    type = "examples"

    def __init__(self, comments, tags, keyword, name, description, line, rows):
        super(Examples, self).__init__(comments, tags, keyword, name,
                                       description, line)
        self.rows = rows

class Step(BasicStatement, Replayable):
    type = "step"

    def __init__(self, comments, keyword, name, line):
        super(Step, self).__init__(comments, keyword, name, line)
        self.rows = None
        self.doc_string = None

    def line_range(self):
        lrange = super(Step, self).line_range()
        if self.rows:
            return (lrange[0], self.rows[-1].line)
        elif self.doc_string:
            return (lrange[0], self.doc_string.line_range()[1])
        return lrange

    def outline_args(self):
        start = 0
        end = 0
        arguments = []
        while True:
            start = self.name.find(u'<', end)
            if start == -1:
                break
            end = self.name.find(u'>', start)
            arguments.append(Argument(start, self.name[start:end + 1]))
        return arguments

class Comment(Dictable):
    def __init__(self, value, line):
        self.value = ensure_unicode(value)
        self.line = line

class Tag(Dictable):
    def __init__(self, name, line):
        self.name = ensure_unicode(name)
        self.line = line

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

class DocString(Dictable):
    def __init__(self, content_type, value, line):
        self.content_type = ensure_unicode(content_type)
        self.value = ensure_unicode(value)
        self.line = line

    def line_range(self):
        line_count = len(self.value.splitlines())
        return (self.line, self.line + line_count + 1)

class Row(Dictable):
    def __init__(self, comments, cells, line):
        self.comments = comments
        self.cells = [ensure_unicode(c) for c in cells]
        self.line = line

class Match(Dictable, Replayable):
    type = "match"

    def __init__(self, arguments, location):
        self.arguments = arguments
        self.location = location

class Result(Dictable, Replayable):
    type = "result"

    def __init__(self, status, duration, error_message):
        self.status = ensure_unicode(status)
        self.duration = duration
        self.error_message = ensure_unicode(error_message)
