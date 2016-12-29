#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Support functionality to simplify the setup for behave tests.

.. sourcecode:: python

    # -- FILE: features/environment.py
    from behave4cmd0.setup_command_shell import setup_command_shell_processors4behave

    def before_all(context):
        setup_command_shell_processors4behave()
"""

from __future__ import absolute_import
from .command_shell import Command
from .command_shell_proc import BehaveWinCommandOutputProcessor

def setup_command_shell_processors4behave():
    Command.POSTPROCESSOR_MAP["behave"] = []
    for processor_class in [BehaveWinCommandOutputProcessor]:
        if processor_class.enabled:
            processor = processor_class()
            Command.POSTPROCESSOR_MAP["behave"].append(processor)
