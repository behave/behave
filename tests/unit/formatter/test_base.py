# -*- coding: UTF-8
"""
Unit tests for :mod:`behave.formatter.base` module.
"""

from __future__ import absolute_import, print_function
import codecs
import os
import sys

import six
import chardet
import pytest

from behave.formatter.base import StreamOpener

if six.PY2:
    # -- NEEDED-FOR: Path should be similar to Python3 implementation.
    from pathlib2 import Path
else:
    from pathlib import Path


# -----------------------------------------------------------------------------
# TEST SUPPORT
# -----------------------------------------------------------------------------
def assert_same_encoding(encoding1, encoding2):
    codec_info1 = codecs.lookup(encoding1)
    codec_info2 = codecs.lookup(encoding2)
    assert codec_info1.name == codec_info2.name

def assert_that_file_has_encoding(filename, encoding):
    path = Path(filename)
    assert path.exists(), "FileNotFound: {filename}".format(filename=filename)
    file_data = chardet.detect(path.read_bytes())
    actual_encoding = file_data.get('encoding')
    print("filename={filename}, chardet,file_data={file_data}".format(
          filename=filename, file_data=file_data))
    assert_same_encoding(actual_encoding, encoding)

def _setup_console_encoding_on_windows(encoding):
    encoding = encoding.lower()
    code_page = None
    if "utf-8" in encoding or encoding == "cp65001":
        code_page = "65001"
        os.environ["LANG"] = "en_US.UTF-8"
        os.environ["PYTHONUTF8"] = "1"
    if encoding.startswith("windows-"):
        code_page = encoding.replace("windows-", "")
    elif encoding.startswith("cp"):
        code_page = encoding[2:]

    os.environ["PYTHONIOENCODING"] = encoding
    os.system("chcp {code_page}".format(code_page=code_page))

def _setup_console_encoding_on_posix(encoding, language=None):
    # if encoding == "cp65001":
    #    encoding = "utf-8"
    encoding_value = encoding
    if language is None:
        language = "en_US"
    if language:
        encoding_value = "{language}.{encoding}".format(
            language=language, encoding=encoding
        )

    os.environ["LANG"] = encoding_value
    os.environ["LC_ALL"] = encoding_value
    os.environ["LC_CTYPE"] = encoding_value
    os.environ["PYTHONIOENCODING"] = encoding

def select_setup_console_encoding():
    if sys.platform == "win32":
        return _setup_console_encoding_on_windows
    # -- OTHERWISE:
    return _setup_console_encoding_on_posix

@pytest.fixture(scope="function")
def clean_environment():
    """
    Ensures that the environment is cleaned after each test.
    """
    current_env = os.environ.copy()
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(current_env)


# -----------------------------------------------------------------------------
# TEST SUITE
# -----------------------------------------------------------------------------
class TestStreamOpener(object):
    EXAMPLE_TEXT = u"Nur Äarger mit Jürgen"
    ENCODINGS = [
        "UTF-8", "UTF-8-sig",  # UTF-8 with BOM
        "latin-1", "ISO-8859-1",
        "cp1250", "cp65001" # aka: UTF-8
    ]

    def test_open_with_file_without_encoding(self, tmp_path):
        # -- HINT: Path needs string-conversion for Python2/Python3 compatibility.
        filename = tmp_path/"example_with_default_encoding.txt"
        this_stream = StreamOpener(str(filename))
        this_stream.open()
        this_stream.stream.write(self.EXAMPLE_TEXT)
        this_stream.close()

        encoding = this_stream.default_encoding
        assert_that_file_has_encoding(filename, encoding)

    @pytest.mark.parametrize("encoding", ENCODINGS)
    def test_open_with_file_with_encoding(self, tmp_path, encoding, clean_environment):
        setup_console_encoding = select_setup_console_encoding()
        setup_console_encoding(encoding)
        filename = tmp_path/"example_with_{encoding}.txt".format(
            encoding=encoding.lower()
        )
        # -- HINT: Path needs string-conversion for Python2/Python3 compatibility.
        this_stream = StreamOpener(str(filename))
        this_stream.open()
        this_stream.stream.write(self.EXAMPLE_TEXT)
        this_stream.close()

        encoding = this_stream.default_encoding
        assert_that_file_has_encoding(filename, encoding)
