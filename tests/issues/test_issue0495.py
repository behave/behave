# -*- coding: UTF-8 -*-
"""
Explore issue #495.
HINT: Problem can be reproduced if you remove encoding-declaration from above.

::
    Traceback (most recent call last):
      File "/usr/local/bin/behave", line 11, in <module>
        sys.exit(main())
      File "/usr/local/lib/python2.7/dist-packages/behave/__main__.py", line 109, in main
        failed = runner.run()
        ...
      File "/usr/local/lib/python2.7/dist-packages/behave/model.py", line 919, in run
        runner.run_hook('after_scenario', runner.context, self)
      File "/usr/local/lib/python2.7/dist-packages/behave/runner.py", line 405, in run_hook
        self.hooks[name](context, *args)
      File "/mnt/work/test/lib/logcapture.py", line 22, in f
        v = h.getvalue()
      File "/usr/local/lib/python2.7/dist-packages/behave/log_capture.py", line 99, in getvalue
        return '\n'.join(self.formatter.format(r) for r in self.buffer)
    UnicodeDecodeError: 'ascii' codec can't decode byte 0xc2 in position 3807: ordinal not in range(128)
"""

from behave.log_capture import capture
from behave.configuration import Configuration
import logging
import pytest

# -----------------------------------------------------------------------------
# TEST SUPPORT
# -----------------------------------------------------------------------------
# def ensure_logging_setup():
#    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

class SimpleContext(object): pass


# -----------------------------------------------------------------------------
# TESTS:
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("log_message", [
    u"Hello Alice",             # case: unproblematic (GOOD CASE)
    u"Ärgernis ist überall",    # case: unicode-string
    "Ärgernis",                 # case: byte-string (use encoding-declaration above)
])
def test_issue(log_message):
    @capture(level=logging.INFO)
    def hook_after_scenario(context, message):
        logging.warn(message)
        raise RuntimeError()

    # -- PREPARE:
    # ensure_logging_setup()
    context = SimpleContext()
    context.config = Configuration("", load_config=False,
        log_capture=True,
        logging_format="%(levelname)s: %(message)s",
        logging_level=logging.INFO
    )
    context.config.setup_logging()

    # -- EXECUTE:
    with pytest.raises(RuntimeError):
        hook_after_scenario(context, log_message)
    # EXPECT: UnicodeError is not raised
