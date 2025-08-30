"""
Unit tests for :mod:`behave.pathutil`.
"""
import sys
from pathlib import Path
from behave.pathutil import select_subdirectories
import pytest


# -----------------------------------------------------------------------------
# TEST SUPPORT
# -----------------------------------------------------------------------------
THIS_FILE = Path(__file__)
HERE = THIS_FILE.parent
PYTHON_VERSION = sys.version_info[:2]

class BadClass:
    pass


def ensure_directory_exists(directory):
    # -- SPECIAL CASE FOR: Python27 pathlib.Path
    directory = Path(str(directory))
    if directory.is_dir():
        return
    directory.mkdir(parents=True)
    # -- PY27 NOT-SUPPORTED: directory.mkdir(parents=True, exist_ok=True)

def ensure_many_directories_exist(directories):
    for directory in directories:
        ensure_directory_exists(directory)

def assert_paths_are_equal(actual_paths, expected_paths):
    actual_paths1 = [str(p) for p in actual_paths]
    expected_paths1 = [str(p) for p in expected_paths]
    assert actual_paths1 == expected_paths1


# -----------------------------------------------------------------------------
# TEST SUITE
# -----------------------------------------------------------------------------
def test_select_subdirectories_with_one_level_subdirs(tmp_path):
    this_directory = tmp_path/"some_directory"
    subdirs = [this_directory/"subdir_1", this_directory/"subdir_2"]
    ensure_many_directories_exist(subdirs)
    selected = select_subdirectories(this_directory)
    expected = subdirs
    assert_paths_are_equal(selected, expected)

def test_select_subdirectories_with_many_level_subdirs(tmp_path):
    this_directory = tmp_path/"some_directory"
    subdirs = [
        this_directory/"subdir_1/subdir_12",
        this_directory/"subdir_2/",
        this_directory/"subdir_3/subdir_31/subdir_32",
    ]
    ensure_many_directories_exist(subdirs)
    selected = select_subdirectories(this_directory)
    expected = [
        this_directory/"subdir_1",
        this_directory/"subdir_1/subdir_12",
        this_directory/"subdir_2",
        this_directory/"subdir_3",
        this_directory/"subdir_3/subdir_31",
        this_directory/"subdir_3/subdir_31/subdir_32",
    ]
    assert_paths_are_equal(selected, expected)

def test_select_subdirectories_using_nonrecursive_mode(tmp_path):
    this_directory = tmp_path/"some_directory"
    subdirs = [
        this_directory/"subdir_1",
        this_directory/"subdir_2/subdir_21",
    ]
    ensure_many_directories_exist(subdirs)
    selected = select_subdirectories(this_directory, recursive=False)
    expected = [
        this_directory/"subdir_1",
        this_directory/"subdir_2",
    ]
    assert_paths_are_equal(selected, expected)

def test_select_subdirectories_with_many_are_sorted(tmp_path):
    # -- ENSURE: Sorted in ascending order
    this_directory = tmp_path/"some_directory"
    subdirs = [
        this_directory/"subdir_2",
        this_directory/"subdir_1"
    ]
    ensure_many_directories_exist(subdirs)
    selected = select_subdirectories(this_directory)
    expected = sorted(subdirs)
    assert_paths_are_equal(selected, expected)

def test_select_subdirectories_with_path_param(tmp_path):
    this_directory = tmp_path/"some_directory"
    subdirs = [this_directory/"subdir_1", this_directory/"subdir_2"]
    ensure_many_directories_exist(subdirs)
    # -- SPECIAL CASE: Python 2.7
    # selected = select_subdirectories(Path(this_directory))
    selected = select_subdirectories(Path(str(this_directory)))
    expected = subdirs
    assert_paths_are_equal(selected, expected)

def test_select_subdirectories_with_string_param(tmp_path):
    this_directory = tmp_path/"some_directory"
    subdirs = [this_directory/"subdir_1", this_directory/"subdir_2"]
    ensure_many_directories_exist(subdirs)
    selected = select_subdirectories(str(this_directory))
    expected = subdirs
    assert_paths_are_equal(selected, expected)

@pytest.mark.parametrize("bad_type, bad_directory", [
    ("bytes", str(HERE.relative_to(Path.cwd())).encode("UTF-8")),
    ("int", 123),
    ("None", None),
    ("BadClass", BadClass()),
])
def test_select_subdirectories_with_other_type_raises_error(tmp_path, bad_type, bad_directory):
    if bad_type == "bytes" and PYTHON_VERSION < (3, 0):
        # -- SPECIAL CASE: bytes is acceptable type in Python 2.7
        _ = select_subdirectories(bad_directory)
    else:
        # -- BAD-TYPE CASES:
        with pytest.raises(TypeError):
            _ = select_subdirectories(bad_directory)


def test_select_subdirectories_with_nonexistent_directory_returns_empty_list():
    non_existing_directory = HERE/"non_existing_directory"
    assert not non_existing_directory.exists()
    subdirs = select_subdirectories(non_existing_directory)
    assert subdirs == []
    assert len(subdirs) == 0

def test_select_subdirectories_with_file_raises_error():
    with pytest.raises(ValueError):
        assert THIS_FILE.is_file()
        _ = select_subdirectories(THIS_FILE, recursive=False)
