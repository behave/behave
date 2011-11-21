import re

from behave import model

class Matcher(object):
    def __init__(self, func, string):
        self.func = func
        self.string = string
        
    def check_match(self, step):
        raise NotImplemented

    def match(self, step):
        result = self.check_match(step)
        if result is False:
            return None
        return model.Match(self.func, result)

class RegexMatcher(Matcher):
    def __init__(self, func, regex):
        super(RegexMatcher, self).__init__(func, regex)
        self.regex = re.compile(self.string)
    
    def check_match(self, step):
        m = self.regex.match(step)
        if not m:
            return False

        groupindex = dict((y, x) for x, y in self.regex.groupindex.items())
        args = []
        for index, group in enumerate(m.groups()):
            index += 1
            name = groupindex.get(index, None)
            args.append(model.Argument(m.start(index), group, name))
        
        return args

matcher_mapping = {
    're': RegexMatcher,
}

default_matcher = 're'

def get_matcher(match, string):
    return matcher_mapping[default_matcher](match, string)
