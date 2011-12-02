import logging
from behave import *

spam_log = logging.getLogger('spam')
ham_log = logging.getLogger('ham')

@given("I am testing stuff")
def step(context):
    context.testing_stuff = True

@given("some stuff is set up")
def step(context):
    context.stuff_set_up = True

@given("stuff has been set up")
def step(context):
    assert context.testing_stuff is True
    assert context.stuff_set_up is True

@when("I exercise it work")
def step(context):
    spam_log.error('logging!')
    ham_log.error('logging!')

@then("it will work")
def step(context):
    pass

@given("some text {prefix}")
def step(context, prefix):
    context.prefix = prefix

@when('we add some text {suffix}')
def step(context, suffix):
    context.combination = context.prefix + suffix

@then('we should get the {combination}')
def step(context, combination):
    assert context.combination == combination

@given('some body of text')
def step(context):
    assert context.text
    context.saved_text = context.text

TEXT = '''   Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed
do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut
enim ad minim veniam, quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat.'''
@then('the text is as expected')
def step(context):
    assert context.saved_text, 'context.saved_text is %r!!' % (context.saved_text, )
    context.saved_text.assert_equals(TEXT)

@then('the text is as expected')
def step(context):
    assert context.saved_text, 'context.saved_text is %r!!' % (context.saved_text, )
    assert context.saved_text == TEXT, '%r != expected %r' %(context.saved_text, TEXT)

@given('some initial data')
def step(context):
    assert context.table
    context.saved_table = context.table

TABLE_DATA = [
    dict(name='Barry', department='Beer Cans'),
    dict(name='Pudey', department='Silly Walks'),
    dict(name='Two-Lumps', department='Silly Walks'),
]
@then('we will have the expected data')
def step(context):
    assert context.saved_table, 'context.saved_table is %r!!' % (context.saved_table, )
    for expected, got in zip(TABLE_DATA, iter(context.saved_table)):
        assert expected['name'] == got['name']
        assert expected['department'] == got['department']

