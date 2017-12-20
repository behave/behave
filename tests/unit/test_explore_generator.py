# -*- coding: UTF-8 -*-
"""
Explore contextmanager/generator behaviour when:
* setup step raises error (generator step)
* with-block raises error 
"""

import pytest
from contextlib import contextmanager


class TestContextManager(object):
    def test_when_setup_raises_error_then_cleanup_isnot_called(self):
        @contextmanager
        def foo(checkpoints):
            checkpoints.append("foo.setup.begin")
            raise RuntimeError("OOPS")
            checkpoints.append("foo.setup.done")
            yield
            checkpoints.append("foo.cleanup")

        checkpoints = []
        with pytest.raises(RuntimeError):
            with foo(checkpoints):
                checkpoints.append("foo.with-block")

        assert checkpoints == ["foo.setup.begin"]

    def test_with_try_finally_when_setup_raises_error_then_cleanup_is_called(self):
        @contextmanager
        def foo(checkpoints):
            try:
                checkpoints.append("foo.setup.begin")
                raise RuntimeError("OOPS")
                checkpoints.append("foo.setup.done")
                yield
            finally:
                checkpoints.append("foo.cleanup")

        checkpoints = []
        with pytest.raises(RuntimeError):
            with foo(checkpoints):
                checkpoints.append("foo.with-block")

        assert checkpoints == ["foo.setup.begin", "foo.cleanup"]


class TestGenerator(object):
    def test_when_setup_raises_error_then_cleanup_isnot_called(self):
        def foo(checkpoints):
            checkpoints.append("foo.setup.begin")
            raise RuntimeError("OOPS")
            checkpoints.append("foo.setup.done")
            yield
            checkpoints.append("foo.cleanup")

        checkpoints = []
        with pytest.raises(RuntimeError):
            for iter in foo(checkpoints):
                checkpoints.append("foo.with-block")

        assert checkpoints == ["foo.setup.begin"]

    def test_with_try_finally_when_setup_raises_error_then_cleanup_is_called(self):
        def foo(checkpoints):
            try:
                checkpoints.append("foo.setup.begin")
                raise RuntimeError("OOPS")
                checkpoints.append("foo.setup.done")
                yield
            finally:
                checkpoints.append("foo.cleanup")

        checkpoints = []
        with pytest.raises(RuntimeError):
            for iter in foo(checkpoints):
                checkpoints.append("foo.with-block")

        assert checkpoints == ["foo.setup.begin", "foo.cleanup"]
