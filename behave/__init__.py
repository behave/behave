'''behave is behaviour-driven development, Python style

Behavior-driven development (or BDD) is an agile software development
technique that encourages collaboration between developers, QA and
non-technical or business participants in a software project.

*behave* uses tests written in a natural language style, backed up by Python
code.

To get started, we recommend the `tutorial`_ and then the `test language`_ and
`api`_ references.

.. _`tutorial`: tutorial.html
.. _`test language`: gherkin.html
.. _`api`: api.html
'''

__version__ = '1.1.0'

from behave.step_registry import *
from behave.matchers import step_matcher

names = 'given when then step'
names = names + ' ' + names.title()
names = names + ' step_matcher'
__all__ = names.split()
