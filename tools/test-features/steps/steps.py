# -*- coding: UTF-8 -*-
# ruff: noqa: F811
from __future__ import absolute_import
import logging
from behave import given, when, then, register_type
from six.moves import zip
from assertpy import assert_that


spam_log = logging.getLogger('spam')
ham_log = logging.getLogger('ham')


@given("I am testing stuff")
def step_impl(context):
    context.testing_stuff = True


@given("some stuff is set up")
def step_impl(context):
    context.stuff_set_up = True


@given("stuff has been set up")
def step_impl(context):
    assert_that(context.testing_stuff).is_equal_to(True)
    assert_that(context.stuff_set_up).is_equal_to(True)


@when("I exercise it work")
def step_impl(context):
    spam_log.error('logging!')
    ham_log.error('logging!')


@then("it will work")
def step_impl(context):
    pass


@given("some text {prefix}")
def step_impl(context, prefix):
    context.prefix = prefix


@when('we add some text {suffix}')
def step_impl(context, suffix):
    context.combination = context.prefix + suffix


@then('we should get the {combination}')
def step_impl(context, combination):
    assert_that(context.combination).is_equal_to(combination)


@given('some body of text')
@given('some body of text:')
def step_impl(context):
    assert context.text
    context.saved_text = context.text


TEXT = '''   Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed
do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut
enim ad minim veniam, quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat.'''


@then('the text is as expected')
def step_impl(context):
    assert context.saved_text, 'context.saved_text is %r!!' % (context.saved_text, )
    assert_that(context.saved_text).is_equal_to(TEXT)


@given('some initial data')
@given('some initial data:')
def step_impl(context):
    assert context.table
    context.saved_table = context.table


TABLE_DATA = [
    dict(name='Barry', department='Beer Cans'),
    dict(name='Pudey', department='Silly Walks'),
    dict(name='Two-Lumps', department='Silly Walks'),
]


@then('we will have the expected data')
def step_impl(context):
    assert context.saved_table, 'context.saved_table is %r!!' % (context.saved_table, )
    for expected, got in zip(TABLE_DATA, iter(context.saved_table)):
        assert_that(expected["name"]).is_equal_to(got["name"])
        assert_that(expected["department"]).is_equal_to(got["department"])


@then('the text is substituted as expected')
def step_impl(context):
    assert context.saved_text, 'context.saved_text is %r!!' % (context.saved_text, )
    expected = TEXT.replace('ipsum', context.active_outline['ipsum'])
    assert_that(context.saved_text).is_equal_to(expected)


TABLE_DATA = [
    dict(name='Barry', department='Beer Cans'),
    dict(name='Pudey', department='Silly Walks'),
    dict(name='Two-Lumps', department='Silly Walks'),
]


@then('we will have the substituted data')
def step_impl(context):
    assert context.saved_table, 'context.saved_table is %r!!' % (context.saved_table, )
    value = context.active_outline['spam']
    expected = value + ' Cans'
    assert context.saved_table[0]['department'] == expected, '%r != %r' % (
        context.saved_table[0]['department'], expected)


@given('the tag "{tag}" is set')
def step_impl(context, tag):
    assert tag in context.tags, '%r NOT present in %r!' % (tag, context.tags)
    if tag == 'spam':
        assert context.is_spammy


@given('the tag "{tag}" is not set')
def step_impl(context, tag):
    assert tag not in context.tags, '%r IS present in %r!' % (tag, context.tags)


@given('a string {argument} an argument')
def step_impl(context, argument):
    context.argument = argument


register_type(custom=lambda s: s.upper())


@given('a string {argument:custom} a custom type')
def step_impl(context, argument):
    context.argument = argument


@then('we get "{argument}" parsed')
def step_impl(context, argument):
    assert_that(context.argument).is_equal_to(argument)

