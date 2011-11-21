from collections import defaultdict

from behave import model

class AttrDict(dict):
    def __getattr__(self, attr):
        return self.__getitem__(attr)

    def __setattr__(self, attr, value):
        return self.__setitem__(attr, value)

class Context(object):
    def __init__(self):
        self._stack = [{}]

    def _push(self):
        self._stack.insert(0, {})

    def _pop(self):
        self._stack.pop(0)

    def _dump(self):
        for level, frame in enumerate(self._stack):
            print 'Level %d' % level
            print repr(frame)

    def __getattr__(self, attr):
        for frame in self._stack:
            if attr in frame:
                return frame[attr]
        msg = "'{0}' object has no attribute '{1}'"
        msg = msg.format(self.__class__.__name__, attr)
        raise AttributeError(msg)

    def __setattr__(self, attr, value):
        if attr == '_stack':
            self.__dict__['_stack'] = value
            return

        frame = self.__dict__['_stack'][0]
        frame[attr] = value

class StepRegistry(object):
    def __init__(self):
        self.steps = {
            'given': [],
            'when': [],
            'then': [],
            'step': [],
        }

    def add_definition(self, keyword, regex, func):
        match = model.Match(func)
        self.steps[keyword.lower()].append((regex, match))

    def find_match(self, step):
        candidates = self.steps[step.step_type]
        if step.step_type is not 'step':
            candidates += self.steps['step']

        for regex, match in candidates:
            m = regex.match(step.name)
            if not m:
                continue

            groupindex = dict((y, x) for x, y in regex.groupindex.items())
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
