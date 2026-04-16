"""Shared fixtures for reporter tests."""

from unittest.mock import Mock

import pytest

from behave.model import Feature
from behave.model_type import Status


@pytest.fixture
def mock_config(tmp_path):
    config = Mock()
    config.junit_directory = str(tmp_path)
    config.paths = []
    config.base_dir = "."
    config.userdata = {}
    config.show_skipped = True
    return config


@pytest.fixture
def feature():
    feature = Feature(
        filename="features/test.feature",
        line=1,
        keyword="Feature",
        name="Test Feature",
    )
    feature._status = Status.passed
    return feature
