# -*- coding: UTF-8 -*-
# pylint: disable=too-many-lines, line-too-long

from __future__ import absolute_import, print_function, with_statement
from collections import defaultdict
import os.path
import sys
import unittest
import six
from six import StringIO
import pytest
from mock import Mock, patch
from behave import runner_util
from behave import runner
from behave.exception import ConfigError
from behave.formatter.base import StreamOpener



def create_mock_config():
    config = Mock()
    config.steps_dir = "steps"
    config.environment_file = "environment.py"
    return config


class TestRunner(object):
    # pylint: disable=invalid-name, no-self-use

    def test_load_hooks_execfiles_hook_file(self):
        with patch("behave.runner.exec_file") as ef:
            with patch("os.path.exists") as exists:
                exists.return_value = True
                base_dir = "fake/path"
                hooks_path = os.path.join(base_dir, "environment.py")

                r = runner.Runner(create_mock_config())
                r.base_dir = base_dir
                r.load_hooks()

                exists.assert_called_with(hooks_path)
                ef.assert_called_with(hooks_path, r.hooks)

    def test_run_hook_runs_a_hook_that_exists(self):
        config = Mock()
        r = runner.Runner(config)
        # XXX r.config = Mock()
        r.config.stdout_capture = False
        r.config.stderr_capture = False
        r.config.dry_run = False
        r.hooks["before_lunch"] = hook = Mock()
        args = (runner.Context(Mock()), Mock(), Mock())
        r.run_hook("before_lunch", *args)

        hook.assert_called_with(*args)

    def test_run_hook_does_not_runs_a_hook_that_exists_if_dry_run(self):
        r = runner.Runner(None)
        r.config = Mock()
        r.config.dry_run = True
        r.hooks["before_lunch"] = hook = Mock()
        args = (runner.Context(Mock()), Mock(), Mock())
        r.run_hook("before_lunch", *args)

        assert len(hook.call_args_list) == 0

    def test_setup_capture_creates_stringio_for_stdout(self):
        r = runner.Runner(Mock())
        r.config.stdout_capture = True
        r.config.log_capture = False
        r.context = Mock()

        r.setup_capture()

        assert r.capture_controller.stdout_capture is not None
        assert isinstance(r.capture_controller.stdout_capture, StringIO)

    def test_setup_capture_does_not_create_stringio_if_not_wanted(self):
        r = runner.Runner(Mock())
        r.config.stdout_capture = False
        r.config.stderr_capture = False
        r.config.log_capture = False

        r.setup_capture()

        assert r.capture_controller.stdout_capture is None

    @patch("behave.capture.LoggingCapture")
    def test_setup_capture_creates_memory_handler_for_logging(self, handler):
        r = runner.Runner(Mock())
        r.config.stdout_capture = False
        r.config.log_capture = True
        r.context = Mock()

        r.setup_capture()

        assert r.capture_controller.log_capture is not None
        handler.assert_called_with(r.config)
        r.capture_controller.log_capture.inveigle.assert_called_with()

    def test_setup_capture_does_not_create_memory_handler_if_not_wanted(self):
        r = runner.Runner(Mock())
        r.config.stdout_capture = False
        r.config.stderr_capture = False
        r.config.log_capture = False

        r.setup_capture()

        assert r.capture_controller.log_capture is None

    def test_start_stop_capture_switcheroos_sys_stdout(self):
        old_stdout = sys.stdout
        sys.stdout = new_stdout = Mock()

        r = runner.Runner(Mock())
        r.config.stdout_capture = True
        r.config.log_capture = False
        r.context = Mock()

        r.setup_capture()
        r.start_capture()

        assert sys.stdout == r.capture_controller.stdout_capture

        r.stop_capture()

        assert sys.stdout == new_stdout

        sys.stdout = old_stdout

    def test_start_stop_capture_leaves_sys_stdout_alone_if_off(self):
        r = runner.Runner(Mock())
        r.config.stdout_capture = False
        r.config.log_capture = False

        old_stdout = sys.stdout

        r.start_capture()

        assert sys.stdout == old_stdout

        r.stop_capture()

        assert sys.stdout == old_stdout

    def test_teardown_capture_removes_log_tap(self):
        r = runner.Runner(Mock())
        r.config.stdout_capture = False
        r.config.log_capture = True

        r.capture_controller.log_capture = Mock()

        r.teardown_capture()

        r.capture_controller.log_capture.abandon.assert_called_with()

    def test_exec_file(self, tmp_path):
        filename = str(tmp_path/"example.py")
        with open(filename, "w") as f:
            f.write("spam = __file__\n")
        my_globals = {}
        my_locals = {}
        runner_util.exec_file(filename, my_globals, my_locals)
        assert "__file__" in my_locals
        # pylint: disable=too-many-format-args
        assert "spam" in my_locals, '"spam" variable not set in locals (%r)' % (my_globals, my_locals)
        # pylint: enable=too-many-format-args
        assert my_locals["spam"] == filename

    def test_run_returns_true_if_everything_passed(self):
        r = runner.Runner(Mock())
        r.setup_capture = Mock()
        r.setup_paths = Mock()
        r.run_with_paths = Mock()
        r.run_with_paths.return_value = True
        assert r.run()

    def test_run_returns_false_if_anything_failed(self):
        r = runner.Runner(Mock())
        r.setup_capture = Mock()
        r.setup_paths = Mock()
        r.run_with_paths = Mock()
        r.run_with_paths.return_value = False
        assert not r.run()


class TestRunWithPaths(unittest.TestCase):
    # pylint: disable=invalid-name, no-self-use

    def setUp(self):
        self.config = Mock()
        self.config.reporters = []
        self.config.logging_level = None
        self.config.logging_filter = None
        self.config.outputs = [Mock(), StreamOpener(stream=sys.stdout)]
        self.config.format = ["plain", "progress"]
        self.config.logging_format = None
        self.config.logging_datefmt = None
        self.runner = runner.Runner(self.config)
        self.load_hooks = self.runner.load_hooks = Mock()
        self.load_step_definitions = self.runner.load_step_definitions = Mock()
        self.run_hook = self.runner.run_hook = Mock()
        self.run_step = self.runner.run_step = Mock()
        self.feature_locations = self.runner.feature_locations = Mock()
        self.calculate_summaries = self.runner.calculate_summaries = Mock()

        self.formatter_class = patch("behave.formatter.pretty.PrettyFormatter")
        formatter_class = self.formatter_class.start()
        formatter_class.return_value = self.formatter = Mock()

    def tearDown(self):
        self.formatter_class.stop()

    def test_loads_hooks_and_step_definitions(self):
        self.feature_locations.return_value = []
        self.runner.run_with_paths()

        assert self.load_hooks.called
        assert self.load_step_definitions.called

    def test_runs_before_all_and_after_all_hooks(self):
        # Make runner.feature_locations() and runner.run_hook() the same mock so
        # we can make sure things happen in the right order.
        self.runner.feature_locations = self.run_hook
        self.runner.feature_locations.return_value = []
        self.runner.context = Mock()
        self.runner.run_with_paths()

        assert self.run_hook.call_args_list == [
            ((), {}),
            (("before_all", self.runner.context), {}),
            (("after_all", self.runner.context), {}),
        ]

    @patch("behave.parser.parse_file")
    @patch("os.path.abspath")
    def test_parses_feature_files_and_appends_to_feature_list(self, abspath,
                                                              parse_file):
        feature_locations = ["one", "two", "three"]
        feature = Mock()
        feature.tags = []
        feature.__iter__ = Mock(return_value=iter([]))
        feature.run.return_value = False
        self.runner.feature_locations.return_value = feature_locations
        abspath.side_effect = lambda x: x.upper()
        self.config.lang = "fritz"
        self.config.format = ["plain"]
        self.config.outputs = [StreamOpener(stream=sys.stdout)]
        self.config.output.encoding = None
        self.config.exclude = lambda s: False
        self.config.junit = False
        self.config.summary = False
        parse_file.return_value = feature

        self.runner.run_with_paths()

        expected_parse_file_args = \
            [((x.upper(),), {"language": "fritz"}) for x in feature_locations]
        assert parse_file.call_args_list == expected_parse_file_args
        assert self.runner.features == [feature] * 3


class FsMock(object):
    def __init__(self, *paths):
        self.base = os.path.abspath(".")
        self.sep = os.path.sep

        # This bit of gymnastics is to support Windows. We feed in a bunch of
        # paths in places using FsMock that assume that POSIX-style paths
        # work. This is faster than fixing all of those but at some point we
        # should totally do it properly with os.path.join() and all that.
        def full_split(path):
            bits = []

            while path:
                path, bit = os.path.split(path)
                bits.insert(0, bit)

            return bits

        paths = [os.path.join(self.base, *full_split(path)) for path in paths]
        print(repr(paths))
        self.paths = paths
        self.files = set()
        self.dirs = defaultdict(list)
        separators = [sep for sep in (os.path.sep, os.path.altsep) if sep]
        for path in paths:
            if path[-1] in separators:
                self.dirs[path[:-1]] = []
                d, p = os.path.split(path[:-1])
                while d and p:
                    self.dirs[d].append(p)
                    d, p = os.path.split(d)
            else:
                self.files.add(path)
                d, f = os.path.split(path)
                self.dirs[d].append(f)
        self.calls = []

    def listdir(self, dir):
        # pylint: disable=W0622
        #   W0622   Redefining built-in dir
        self.calls.append(("listdir", dir))
        return self.dirs.get(dir, [])

    def isfile(self, path):
        self.calls.append(("isfile", path))
        return path in self.files

    def isdir(self, path):
        self.calls.append(("isdir", path))
        return path in self.dirs

    def exists(self, path):
        self.calls.append(("exists", path))
        return path in self.dirs or path in self.files

    def walk(self, path, locations=None, followlinks=False):
        if locations is None:
            assert path in self.dirs, "%s not in %s" % (path, self.dirs)
            locations = []
        dirnames = []
        filenames = []
        for e in self.dirs[path]:
            if os.path.join(path, e) in self.dirs:
                dirnames.append(e)
                self.walk(os.path.join(path, e), locations)
            else:
                filenames.append(e)
        locations.append((path, dirnames, filenames))
        return locations

    # utilities that we need
    # pylint: disable=no-self-use
    def dirname(self, path, orig=os.path.dirname):
        return orig(path)

    def abspath(self, path, orig=os.path.abspath):
        return orig(path)

    def join(self, x, y, orig=os.path.join):
        return orig(x, y)

    def split(self, path, orig=os.path.split):
        return orig(path)

    def splitdrive(self, path, orig=os.path.splitdrive):
        return orig(path)


class TestFeatureDirectory(object):
    # pylint: disable=invalid-name, no-self-use

    def test_default_path_no_steps(self):
        config = create_mock_config()
        config.paths = []
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock()

        # will look for a "features" directory and not find one
        with patch("os.path", fs):
            with pytest.raises(ConfigError):
                r.setup_paths()
            # OLD: assert_raises(ConfigError, r.setup_paths)

        assert ("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls
        # ok_(("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls)

    def test_default_path_no_features(self):
        config = create_mock_config()
        config.paths = []
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock("features/steps/")
        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with pytest.raises(ConfigError):
                    r.setup_paths()
                # OLD: assert_raises(ConfigError, r.setup_paths)

    def test_default_path(self):
        config = create_mock_config()
        config.paths = []
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock("features/steps/", "features/foo.feature")

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with r.path_manager:
                    r.setup_paths()

        assert r.base_dir == os.path.abspath("features")

    def test_supplied_feature_file(self):
        config = create_mock_config()
        config.paths = ["foo.feature"]
        config.verbose = True
        r = runner.Runner(config)
        r.context = Mock()

        fs = FsMock("steps/", "foo.feature")

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with r.path_manager:
                    r.setup_paths()
        assert ("isdir", os.path.join(fs.base, "steps")) in fs.calls
        assert ("isfile", os.path.join(fs.base, "foo.feature")) in fs.calls
        # OLD: ok_(("isdir", os.path.join(fs.base, "steps")) in fs.calls)
        # OLD: ok_(("isfile", os.path.join(fs.base, "foo.feature")) in fs.calls)

        assert r.base_dir == fs.base

    def test_supplied_feature_file_no_steps(self):
        config = create_mock_config()
        config.paths = ["foo.feature"]
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock("foo.feature")

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with r.path_manager:
                    with pytest.raises(ConfigError):
                        r.setup_paths()
                    # OLD: assert_raises(ConfigError, r.setup_paths)

    def test_supplied_feature_directory(self):
        config = create_mock_config()
        config.paths = ["spam"]
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock("spam/", "spam/steps/", "spam/foo.feature")

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with r.path_manager:
                    r.setup_paths()

        assert ("isdir", os.path.join(fs.base, "spam", "steps")) in fs.calls
        # OLD ok_(("isdir", os.path.join(fs.base, "spam", "steps")) in fs.calls)

        assert r.base_dir == os.path.join(fs.base, "spam")

    def test_supplied_feature_directory_no_steps(self):
        config = create_mock_config()
        config.paths = ["spam"]
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock("spam/", "spam/foo.feature")

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with pytest.raises(ConfigError):
                    r.setup_paths()
                # OLD: assert_raises(ConfigError, r.setup_paths)

        assert ("isdir", os.path.join(fs.base, "spam", "steps")) in fs.calls
        # OLD: ok_(("isdir", os.path.join(fs.base, "spam", "steps")) in fs.calls)

    def test_supplied_feature_directory_missing(self):
        config = create_mock_config()
        config.paths = ["spam"]
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock()

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with pytest.raises(ConfigError):
                    r.setup_paths()
                # OLD: assert_raises(ConfigError, r.setup_paths)


class TestFeatureDirectoryLayout2(object):
    # pylint: disable=invalid-name, no-self-use

    def test_default_path(self):
        config = create_mock_config()
        config.paths = []
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock(
            "features/",
            "features/steps/",
            "features/group1/",
            "features/group1/foo.feature",
        )

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with r.path_manager:
                    r.setup_paths()

        assert r.base_dir == os.path.abspath("features")

    def test_supplied_root_directory(self):
        config = create_mock_config()
        config.paths = ["features"]
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock(
            "features/",
            "features/group1/",
            "features/group1/foo.feature",
            "features/steps/",
        )

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with r.path_manager:
                    r.setup_paths()

        # OLD: ok_(("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls)
        assert ("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls
        assert r.base_dir == os.path.join(fs.base, "features")

    def test_supplied_root_directory_no_steps(self):
        config = create_mock_config()
        config.paths = ["features"]
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock(
            "features/",
            "features/group1/",
            "features/group1/foo.feature",
        )

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with r.path_manager:
                    with pytest.raises(ConfigError):
                        r.setup_paths()
                    # OLD: assert_raises(ConfigError, r.setup_paths)

        # OLD: ok_(("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls)
        assert ("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls
        assert r.base_dir is None


    def test_supplied_feature_file(self):
        config = create_mock_config()
        config.paths = ["features/group1/foo.feature"]
        config.verbose = True
        r = runner.Runner(config)
        r.context = Mock()

        fs = FsMock(
            "features/",
            "features/group1/",
            "features/group1/foo.feature",
            "features/steps/",
        )

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with r.path_manager:
                    r.setup_paths()

        # OLD: ok_(("isdir", os.path.join(fs.base, "features", "steps"))  in fs.calls)
        # OLD: ok_(("isfile", os.path.join(fs.base, "features", "group1", "foo.feature")) in fs.calls)
        assert ("isdir", os.path.join(fs.base, "features", "steps"))  in fs.calls
        assert ("isfile", os.path.join(fs.base, "features", "group1", "foo.feature")) in fs.calls
        assert r.base_dir == fs.join(fs.base, "features")

    def test_supplied_feature_file_no_steps(self):
        config = create_mock_config()
        config.paths = ["features/group1/foo.feature"]
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock(
            "features/",
            "features/group1/",
            "features/group1/foo.feature",
        )

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with r.path_manager:
                    with pytest.raises(ConfigError):
                        r.setup_paths()
                    # OLD assert_raises(ConfigError, r.setup_paths)

    def test_supplied_feature_directory(self):
        config = create_mock_config()
        config.paths = ["features/group1"]
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock(
            "features/",
            "features/group1/",
            "features/group1/foo.feature",
            "features/steps/",
        )

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with r.path_manager:
                    r.setup_paths()

        # OLD: ok_(("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls)
        assert ("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls
        assert r.base_dir == os.path.join(fs.base, "features")


    def test_supplied_feature_directory_no_steps(self):
        config = create_mock_config()
        config.paths = ["features/group1"]
        config.verbose = True
        r = runner.Runner(config)

        fs = FsMock(
            "features/",
            "features/group1/",
            "features/group1/foo.feature",
        )

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with pytest.raises(ConfigError):
                    r.setup_paths()
                # OLD: assert_raises(ConfigError, r.setup_paths)

        # OLD: ok_(("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls)
        assert ("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls
