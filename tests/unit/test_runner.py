# -*- coding: UTF-8 -*-
# pylint: disable=too-many-lines, line-too-long

from __future__ import absolute_import, print_function, with_statement
from collections import defaultdict
import os.path
import sys
import unittest
from six import StringIO
import pytest
from mock import Mock, patch
from behave import runner_util
from behave.runner import Context, Runner
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

                runner = Runner(create_mock_config())
                runner.base_dir = base_dir
                runner.load_hooks()

                exists.assert_called_with(hooks_path)
                ef.assert_called_with(hooks_path, runner.hooks)

    def test_run_hook_runs_a_hook_that_exists(self):
        config = Mock()
        runner = Runner(config)
        context = Context(runner)
        runner.config.capture = False
        runner.config.capture_stdout = False
        runner.config.capture_stderr = False
        runner.config.capture_log = False
        runner.config.dry_run = False
        hook = Mock()
        runner.hooks["before_lunch"] = hook
        statement = Mock()
        statement.error_message = ""

        runner.context = context
        runner.run_hook("before_lunch", statement)
        call_args = (context, statement)
        hook.assert_called_with(*call_args)

    def test_run_hook_does_not_runs_a_hook_that_exists_if_dry_run(self):
        config = Mock()
        config.dry_run = True
        hook = Mock()
        runner = Runner(config=config)
        runner.hooks["before_lunch"] = hook

        statement = Mock()
        runner.run_hook("before_lunch", statement)
        assert len(hook.call_args_list) == 0

    def test_setup_capture_creates_stringio_for_stdout(self):
        runner = Runner(Mock())
        runner.config.capture_stdout = True
        runner.config.capture_log = False
        runner.context = Mock()

        runner.setup_capture()

        assert runner.capture_controller.capture_stdout is not None
        assert isinstance(runner.capture_controller.capture_stdout, StringIO)

    def test_setup_capture_does_not_create_stringio_if_not_wanted(self):
        runner = Runner(Mock())
        runner.config.capture_stdout = False
        runner.config.capture_stderr = False
        runner.config.capture_log = False

        runner.setup_capture()

        assert runner.capture_controller.capture_stdout is None

    @patch("behave.capture.LoggingCapture")
    def test_setup_capture_creates_memory_handler_for_logging(self, handler):
        runner = Runner(Mock())
        runner.config.capture_stdout = False
        runner.config.capture_log = True
        runner.context = Mock()

        runner.setup_capture()

        assert runner.capture_controller.capture_log is not None
        handler.assert_called_with(runner.config)
        runner.capture_controller.capture_log.inveigle.assert_called_with()

    def test_setup_capture_does_not_create_memory_handler_if_not_wanted(self):
        runner = Runner(Mock())
        runner.config.capture_stdout = False
        runner.config.capture_stderr = False
        runner.config.capture_log = False

        runner.setup_capture()

        assert runner.capture_controller.capture_log is None

    def test_start_stop_capture_switcheroos_sys_stdout(self):
        old_stdout = sys.stdout
        sys.stdout = new_stdout = Mock()

        runner = Runner(Mock())
        runner.config.capture_stdout = True
        runner.config.capture_log = False
        runner.context = Mock()

        runner.setup_capture()
        runner.start_capture()

        assert sys.stdout == runner.capture_controller.capture_stdout

        runner.stop_capture()

        assert sys.stdout == new_stdout

        sys.stdout = old_stdout

    def test_start_stop_capture_leaves_sys_stdout_alone_if_off(self):
        runner = Runner(Mock())
        runner.config.capture_stdout = False
        runner.config.capture_log = False

        old_stdout = sys.stdout

        runner.start_capture()

        assert sys.stdout == old_stdout

        runner.stop_capture()

        assert sys.stdout == old_stdout

    def test_teardown_capture_removes_log_tap(self):
        runner = Runner(Mock())
        runner.config.capture_stdout = False
        runner.config.capture_log = True

        runner.capture_controller.capture_log = Mock()

        runner.teardown_capture()

        runner.capture_controller.capture_log.abandon.assert_called_with()

    def test_exec_file(self, tmp_path):
        filename = str(tmp_path/"example.py")
        with open(filename, "w") as f:
            f.write("spam = __file__\n")
        my_globals = {}
        my_locals = {}
        runner_util.exec_file(filename, my_globals, my_locals)
        assert "__file__" in my_locals
        # pylint: disable=too-many-format-args
        assert "spam" in my_locals, '"spam" variable not set in locals (%r)' % my_locals
        # pylint: enable=too-many-format-args
        assert my_locals["spam"] == filename

    def test_run_returns_true_if_everything_passed(self):
        runner = Runner(Mock())
        runner.setup_capture = Mock()
        runner.setup_paths = Mock()
        runner.run_with_paths = Mock()
        runner.run_with_paths.return_value = True
        assert runner.run()

    def test_run_returns_false_if_anything_failed(self):
        runner = Runner(Mock())
        runner.setup_capture = Mock()
        runner.setup_paths = Mock()
        runner.run_with_paths = Mock()
        runner.run_with_paths.return_value = False
        assert not runner.run()


class TestRunWithPaths(unittest.TestCase):
    # pylint: disable=invalid-name, no-self-use

    def setUp(self):
        config = Mock()
        config.reporters = []
        config.should_capture_hooks = Mock()
        config.should_capture_hooks.return_value = False
        config.logging_level = None
        config.logging_filter = None
        config.outputs = [Mock(), StreamOpener(stream=sys.stdout)]
        config.format = ["plain", "progress"]
        config.logging_format = None
        config.logging_datefmt = None
        config.environment_file = "environment.py"
        runner = Runner(config)
        runner.base_dir = "."

        def __run_hooks_with_capture(hook_name, *args, **kwargs):
            return runner.run_hook(hook_name, *args)

        runner.run_hook = Mock()
        runner.run_hook_with_capture = __run_hooks_with_capture
        runner.run_step = Mock()
        runner.load_hooks = Mock()
        runner.feature_locations = Mock()
        runner.calculate_summaries = Mock()

        self.config = config
        self.runner = runner
        self.load_hooks = runner.load_hooks
        self.load_step_definitions = runner.load_step_definitions = Mock()
        self.feature_locations = runner.feature_locations

        self.formatter = Mock()
        self.formatter_class = patch("behave.formatter.pretty.PrettyFormatter")
        formatter_class = self.formatter_class.start()
        formatter_class.return_value = self.formatter

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
        # self.runner.feature_locations = self.run_hook
        runner = self.runner
        runner.feature_locations = Mock()
        runner.feature_locations.return_value = []
        runner.config.environment_file = "environment.py"
        runner.context = Context(self.runner)
        runner.run_with_paths()

        assert runner.run_hook.call_args_list == [
            (("before_all",), {}),
            (("after_all",), {}),
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
        runner = Runner(config)

        fs = FsMock()

        # will look for a "features" directory and not find one
        with patch("os.path", fs):
            with pytest.raises(ConfigError):
                runner.setup_paths()
            # OLD: assert_raises(ConfigError, runner.setup_paths)

        assert ("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls
        # ok_(("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls)

    def test_default_path_no_features(self):
        config = create_mock_config()
        config.paths = []
        config.verbose = True
        runner = Runner(config)

        fs = FsMock("features/steps/")
        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with pytest.raises(ConfigError):
                    runner.setup_paths()
                # OLD: assert_raises(ConfigError, runner.setup_paths)

    def test_default_path(self):
        config = create_mock_config()
        config.paths = []
        config.verbose = True
        runner = Runner(config)

        fs = FsMock("features/steps/", "features/foo.feature")

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with runner.path_manager:
                    runner.setup_paths()

        assert runner.base_dir == os.path.abspath("features")

    def test_supplied_feature_file(self):
        config = create_mock_config()
        config.paths = ["foo.feature"]
        config.verbose = True
        runner = Runner(config)
        runner.context = Mock()

        fs = FsMock("steps/", "foo.feature")

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with runner.path_manager:
                    runner.setup_paths()
        assert ("isdir", os.path.join(fs.base, "steps")) in fs.calls
        assert ("isfile", os.path.join(fs.base, "foo.feature")) in fs.calls
        # OLD: ok_(("isdir", os.path.join(fs.base, "steps")) in fs.calls)
        # OLD: ok_(("isfile", os.path.join(fs.base, "foo.feature")) in fs.calls)

        assert runner.base_dir == fs.base

    def test_supplied_feature_file_no_steps(self):
        config = create_mock_config()
        config.paths = ["foo.feature"]
        config.verbose = True
        runner = Runner(config)

        fs = FsMock("foo.feature")

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with runner.path_manager:
                    with pytest.raises(ConfigError):
                        runner.setup_paths()
                    # OLD: assert_raises(ConfigError, runner.setup_paths)

    def test_supplied_feature_directory(self):
        config = create_mock_config()
        config.paths = ["spam"]
        config.verbose = True
        runner = Runner(config)

        fs = FsMock("spam/", "spam/steps/", "spam/foo.feature")

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with runner.path_manager:
                    runner.setup_paths()

        assert ("isdir", os.path.join(fs.base, "spam", "steps")) in fs.calls
        # OLD ok_(("isdir", os.path.join(fs.base, "spam", "steps")) in fs.calls)

        assert runner.base_dir == os.path.join(fs.base, "spam")

    def test_supplied_feature_directory_no_steps(self):
        config = create_mock_config()
        config.paths = ["spam"]
        config.verbose = True
        runner = Runner(config)

        fs = FsMock("spam/", "spam/foo.feature")

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with pytest.raises(ConfigError):
                    runner.setup_paths()
                # OLD: assert_raises(ConfigError, runner.setup_paths)

        assert ("isdir", os.path.join(fs.base, "spam", "steps")) in fs.calls
        # OLD: ok_(("isdir", os.path.join(fs.base, "spam", "steps")) in fs.calls)

    def test_supplied_feature_directory_missing(self):
        config = create_mock_config()
        config.paths = ["spam"]
        config.verbose = True
        runner = Runner(config)

        fs = FsMock()

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with pytest.raises(ConfigError):
                    runner.setup_paths()
                # OLD: assert_raises(ConfigError, runner.setup_paths)


class TestFeatureDirectoryLayout2(object):
    # pylint: disable=invalid-name, no-self-use

    def test_default_path(self):
        config = create_mock_config()
        config.paths = []
        config.verbose = True
        runner = Runner(config)

        fs = FsMock(
            "features/",
            "features/steps/",
            "features/group1/",
            "features/group1/foo.feature",
        )

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with runner.path_manager:
                    runner.setup_paths()

        assert runner.base_dir == os.path.abspath("features")

    def test_supplied_root_directory(self):
        config = create_mock_config()
        config.paths = ["features"]
        config.verbose = True
        runner = Runner(config)

        fs = FsMock(
            "features/",
            "features/group1/",
            "features/group1/foo.feature",
            "features/steps/",
        )

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with runner.path_manager:
                    runner.setup_paths()

        # OLD: ok_(("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls)
        assert ("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls
        assert runner.base_dir == os.path.join(fs.base, "features")

    def test_supplied_root_directory_no_steps(self):
        config = create_mock_config()
        config.paths = ["features"]
        config.verbose = True
        runner = Runner(config)

        fs = FsMock(
            "features/",
            "features/group1/",
            "features/group1/foo.feature",
        )

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with runner.path_manager:
                    with pytest.raises(ConfigError):
                        runner.setup_paths()
                    # OLD: assert_raises(ConfigError, runner.setup_paths)

        # OLD: ok_(("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls)
        assert ("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls
        assert runner.base_dir is None


    def test_supplied_feature_file(self):
        config = create_mock_config()
        config.paths = ["features/group1/foo.feature"]
        config.verbose = True
        runner = Runner(config)
        runner.context = Mock()

        fs = FsMock(
            "features/",
            "features/group1/",
            "features/group1/foo.feature",
            "features/steps/",
        )

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with runner.path_manager:
                    runner.setup_paths()

        assert ("isdir", os.path.join(fs.base, "features", "steps"))  in fs.calls
        assert ("isfile", os.path.join(fs.base, "features", "group1", "foo.feature")) in fs.calls
        assert runner.base_dir == fs.join(fs.base, "features")

    def test_supplied_feature_file_no_steps(self):
        config = create_mock_config()
        config.paths = ["features/group1/foo.feature"]
        config.verbose = True
        runner = Runner(config)

        fs = FsMock(
            "features/",
            "features/group1/",
            "features/group1/foo.feature",
        )

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with runner.path_manager:
                    with pytest.raises(ConfigError):
                        runner.setup_paths()
                    # OLD assert_raises(ConfigError, runner.setup_paths)

    def test_supplied_feature_directory(self):
        config = create_mock_config()
        config.paths = ["features/group1"]
        config.verbose = True
        runner = Runner(config)

        fs = FsMock(
            "features/",
            "features/group1/",
            "features/group1/foo.feature",
            "features/steps/",
        )

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with runner.path_manager:
                    runner.setup_paths()

        # OLD: ok_(("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls)
        assert ("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls
        assert runner.base_dir == os.path.join(fs.base, "features")


    def test_supplied_feature_directory_no_steps(self):
        config = create_mock_config()
        config.paths = ["features/group1"]
        config.verbose = True
        runner = Runner(config)

        fs = FsMock(
            "features/",
            "features/group1/",
            "features/group1/foo.feature",
        )

        with patch("os.path", fs):
            with patch("os.walk", fs.walk):
                with pytest.raises(ConfigError):
                    runner.setup_paths()
                # OLD: assert_raises(ConfigError, runner.setup_paths)

        # OLD: ok_(("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls)
        assert ("isdir", os.path.join(fs.base, "features", "steps")) in fs.calls
