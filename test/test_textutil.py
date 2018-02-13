import unittest

from nose import tools

from behave import textutil


class TestTextUtil(unittest.TestCase):

    def test_indent_with_unicode_byte_string(self):
        textutil.indent(['some unicode in another language espa\xc3\xb1ol',
                         'dont fail'], '   ')
