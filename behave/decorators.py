import re
import types

from .runner import hooks, steps

__all__ = 'Given given When when Then then Step step'.split()

def make_wrapper(regex, step_type):
    def wrapper(func):
        steps.add_definition(step_type, re.compile(regex), func)
        return func
    return wrapper

def given(regex):
    return make_wrapper(regex, 'given')
Given = given

def when(regex):
    return make_wrapper(regex, 'when')
When = when

def then(regex):
    return make_wrapper(regex, 'then')
Then = then

def step(regex):
    return make_wrapper(regex, 'step')
Step = step
