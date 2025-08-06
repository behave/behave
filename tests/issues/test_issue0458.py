# -*- coding: UTF-8
"""
Test issue #458:

Traceback (most recent call last):
  File "/usr/local/bin/behave", line 11, in <module>
    sys.exit(main())
  File "/Library/Python/2.7/site-packages/behave/__main__.py", line 123, in main
    print("'Exception %s: %s" % (e.__class__.__name__, text))
UnicodeEncodeError: 'ascii' codec can't encode character  '\u2019' in position 69:
ordinal not in range(128)


    try:
        failed = runner.run()
    except ParserError as e:
        print("'ParseError: %s" % e)
    except ConfigError as e:
        print("'ConfigError: %s" % e)
    except FileNotFoundError as e:
        print("'FileNotFoundError: %s" % e)
    except InvalidFileLocationError as e:
        print("'InvalidFileLocationError: %s" % e)
    except InvalidFilenameError as e:
        print("'InvalidFilenameError: %s" % e)
    except Exception as e:
        # -- DIAGNOSTICS:
        text = _text(e)
        print("'Exception %s: %s" % (e.__class__.__name__, text))
        raise
"""

from behave.textutil import text as _text
import pytest


def raise_exception(exception_class, message):
    raise exception_class(message)

@pytest.mark.parametrize("exception_class, message", [
    (AssertionError, "Ärgernis"),
    (AssertionError, "Ärgernis"),
    (RuntimeError, "Übermut"),
    (RuntimeError, "Übermut"),
])
def test_issue(exception_class, message):
    with pytest.raises(exception_class) as e:
        # runner.run()
        raise_exception(exception_class, message)

    # -- SHOULD NOT RAISE EXCEPTION HERE:
    text = _text(e.value)
    # -- DIAGNOSTICS:
    print("'text"+ text)
    print("'exception: %s" % e)
