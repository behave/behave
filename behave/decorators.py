import re
import types

from .runner import hooks, steps

def Before(func_or_string='scenario'):
    if type(func_or_string) is types.FunctionType:
        hooks.before['scenario'].append(func_or_string)
        return func_or_string

    stage = func_or_string
    def wrapper(func):
        hooks.before[stage].append(func)
        return func

    return wrapper

def After(func_or_string='scenario'):
    if type(func_or_string) is types.FunctionType:
        hooks.after['scenario'].append(func_or_string)
        return func_or_string

    stage = func_or_string
    def wrapper(func):
        hooks.after[stage].append(func)
        return func

    return wrapper

def Given(regex):
    def wrapper(func):
        steps.add_definition('given', re.compile(regex), func)
        return func
    return wrapper

def When(regex):
    def wrapper(func):
        steps.add_definition('when', re.compile(regex), func)
        return func
    return wrapper

def Then(regex):
    def wrapper(func):
        steps.add_definition('then', re.compile(regex), func)
        return func
    return wrapper
