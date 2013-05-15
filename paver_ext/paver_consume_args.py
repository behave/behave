# -*- coding: utf-8 -*-
"""

"""

class Cmdline(object):
    """
    Simplify to process consuming args of a task w/o specifying the command line.
    Splits up into options and args.

    SPECIFICATION:
      * An option starts with a dash ('-') or dashdash ('--').
      * If an option has a value long options should be used, like:
            --my-long-option=value

    EXAMPLE:
        @task
        @consume_args
        def hello(args):
            cmdline = Cmdline.consume(args, default_args=options.default_args)
            ...
    """
    def __init__(self, args=None, options=None):
        self.args = args or []
        self.options = options or []

    def join_args(self, separator=" "):
        return separator.join(self.args)

    def join_options(self, separator=" "):
        return separator.join(self.options)

    @classmethod
    def consume(cls, args, default_args=None, default_options=None):
        args_ = []
        options_ = []
        for arg in args:
            if arg.startswith("-"):
                options_.append(arg)
            else:
                args_.append(arg)
        if not args_:
            args_ = default_args
        if not options_:
            options_ = default_options
        return cls(args_, options_)
