from .runner import steps

__all__ = 'Given given When when Then then Step step'.split()

def make_wrapper(string, step_type):
    def wrapper(func):
        steps.add_definition(step_type, string, func)
        return func
    return wrapper

def given(string):
    return make_wrapper(string, 'given')
Given = given

def when(string):
    return make_wrapper(string, 'when')
When = when

def then(string):
    return make_wrapper(string, 'then')
Then = then

def step(string):
    return make_wrapper(string, 'step')
Step = step
