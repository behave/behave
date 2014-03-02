# -*- coding: utf-8 -*-
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

__version__ = '1.2.4'

from behave.step_registry import *
from behave.matchers import use_step_matcher, step_matcher, register_type

__step_names = 'given when then step Given When Then Step'.split()
__all__ = __step_names + "use_step_matcher step_matcher register_type".split()
