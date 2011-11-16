from collections import defaultdict

from behave import model

class AttrDict(dict):
    def __getattr__(self, attr):
        return self.__getitem__(attr)
    
    def __setattr__(self, attr, value):
        return self.__setitem__(attr, value)
        
class Context(object):
    def __init__(self):
        self.all = AttrDict()
        self.feature = AttrDict()
        self.scenario = AttrDict()
    
    def reset_feature(self):
        self.feature = AttrDict()
    
    def reset_scenario(self):
        self.scenario = AttrDict()

class StepRegistry(object):
    def __init__(self):
        self.steps = {
            'given': [],
            'when': [],
            'then': [],
        }
    
    def add_definition(self, keyword, regex, func):        
        match = model.Match(func)
        self.steps[keyword.lower()].append((regex, match))
    
    def find_match(self, step):
        for regex, match in self.steps[step.step_type.lower()]:
            m = regex.match(step.name)
            if not m:
                continue
                
            groupindex = dict((y, x) for x, y in regex.groupindex)
            args = []
            for index, group in enumerate(m.groups()):
                index += 1
                name = groupindex.get(index, None)
                args.append(model.Argument(m.start(index), group, name))
                            
            return match.with_arguments(args)
            
        return None

class HooksRegistry(object):
    def __init__(self):
        self.before = defaultdict(lambda: [])
        self.after = defaultdict(lambda: [])

        import types

hooks = HooksRegistry()
steps = StepRegistry()
