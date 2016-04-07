# -*- coding: utf-8 -*-

from __future__ import absolute_import
from behave.formatter.base import Formatter

__author__ = 'Graham TerMarsch, Jason Gowan'
__credits__ = ['Graham TerMarsch', 'Jason Gowan']
__email__ = 'jgowan@ziprecruiter.com'


class TapFormatter(Formatter):
    name = 'tap'
    description = 'TAP (Test Anything protocol)'
    indent = ' ' * 2

    def __init__(self, stream, config):
        super(TapFormatter, self).__init__(stream, config)
        self._feature = None
        self._scenario = None
        self.index = { 'feature':0, 'scenario':0, 'step':0 }


    def feature(self, feature):
        # If we're already processing a Feature, output its results
        self._pop_scenario()
        self._pop_feature()

        # Track this Feature
        self.index['feature'] = self.index['feature'] + 1
        self.index['scenario'] = 0
        self.index['step'] = 0
        self._feature = feature

        self._indent_print(0, '# Feature - {}'.format(feature.name))
        self._indent_print(0, '# ... {}'.format(feature.location))


    def scenario(self, scenario):
        # If we're already processing a Scenario, output its results
        self._pop_scenario()

        # Track this Scenario
        self.index['scenario'] = self.index['scenario'] + 1
        self.index['step'] = 0
        self._scenario = scenario
        self._indent_print(1, '# Scenario - {}'.format(scenario.name))
        self._indent_print(1, '# ... {}'.format(scenario.location))


    def result(self, result):
        self.index['step'] = self.index['step'] + 1

        self._tap_print(
            indent_level=2,
            status=self._get_status_prefix(result.status),
            step_number=self.index['step'],
            name=result.keyword + " " + result.name,
            skipped=self._get_test_skipped(result.status),
            duration=result.duration * 1000
        )

        if result.error_message:
            self._indent_print(2, '# {}'.format(result.error_message))


    def eof(self):
        self._pop_scenario()
        self._pop_feature()
        if self.index['feature'] > 0:
            self.stream.write('1..{}'.format(self.index['feature']))
            self.stream.write('\n')
            self.stream.flush()

    def _pop_feature(self):
        if self._feature is not None:
            self._indent_print(1, '1..{}'.format(self.index['scenario']))
            self._tap_print(
                indent_level=0,
                status=self._get_status_prefix(self._feature.status),
                step_number=self.index['feature'],
                name='Feature: ' + self._feature.name,
                skipped=self._get_test_skipped(self._feature.status),
                duration=self._feature.duration * 1000
            )

            self._feature = None


    def _pop_scenario(self):
        if self._scenario is not None:
            plan_suffix = ''
            if self._scenario.status == 'skipped':
                plan_suffix = ' # Skipped'
            self._indent_print(2, '1..{}{}'.format(self.index['step'], plan_suffix))

            self._tap_print(
                indent_level=1,
                status=self._get_status_prefix(self._scenario.status),
                step_number=self.index['scenario'],
                name='Scenario: ' + self._scenario.name,
                skipped=self._get_test_skipped(self._scenario.status),
                duration=self._scenario.duration * 1000
            )

            self._scenario = None


    def _get_status_prefix(self, status):
        if status == 'passed':
            return 'ok'
        if status == 'skipped':
            return 'ok'
        else:
            return 'not ok'


    def _get_test_skipped(self, status):
        if status == 'skipped':
            return 'Skipped '
        else:
            return ''


    def _tap_print(self, indent_level=0, status='not ok', step_number=0, name='UNKNOWN', skipped='', duration=0):
        self._indent_print(
            indent_level,
            '{:<80} # {}{:0.2f} ms'.format(
                '{} {} {}'.format(status, step_number, name),
                skipped,
                duration
            )
        )


    def _indent_print(self, level, string):
        for i in range(0,level):
            self.stream.write(self.indent),
        self.stream.write(string)
        self.stream.write('\n')
        self.stream.flush()
