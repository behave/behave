# -*- encoding: UTF-8 -*-

import os
import sys

if sys.version_info[0] < 3:
    FEATURES = '''Fonctionnalité: testing stuff

  Scénario: test stuff
    Etant donné I am testing stuff
     Alors it should work

  Scénario: test more stuff
    Etant donné I am testing stuff
     Alors it will work
'''.decode('UTF-8')
    def writer(name):
        def f(text):
            open(name, 'w').write(text.encode('UTF-8'))
        return f
else:
    FEATURES = '''Fonctionnalité: testing stuff

  Scénario: test stuff
    Etant donné I am testing stuff
     Alors it should work

  Scénario: test more stuff
    Etant donné I am testing stuff
     Alors it will work
'''
    def writer(name):
        def f(text):
            open(name, 'w', encoding='UTF-8').write(text)
        return f

ENVIRONMENT_PY = '''import logging

def before_all(context):
    logging.basicConfig()
'''

STEPS_PY = '''import logging
from behave import *

spam_log = logging.getLogger('spam')
ham_log = logging.getLogger('ham')

@given("I am testing stuff")
def step(context):
    pass

@then("it should work")
def step(context):
    spam_log.error('logging!')
    ham_log.error('logging!')
    FAIL

@then("it will work")
def step(context):
    pass
'''

os.makedirs('build/lib/features-fr/steps')

writer('build/lib/features-fr/test.feature')(FEATURES)
open('build/lib/features-fr/environment.py', 'w').write(ENVIRONMENT_PY)
open('build/lib/features-fr/steps/steps.py', 'w').write(STEPS_PY)

