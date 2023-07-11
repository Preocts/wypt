from __future__ import annotations

from typing import Any

import pytest

from wypt.database import Database
from wypt.pattern_config import PatternConfig
from wypt.runtime import _Config
from wypt.runtime import Runtime

TEST_CONFIG = "tests/fixture/wypt.toml"
TEST_PATTERNS = {"Basic Email", "Broken Pattern", "Discord Webhook", "JWT Token"}


def test_load_config() -> None:
    runtime = Runtime()

    config = runtime.load_config(TEST_CONFIG)

    assert config is runtime._config
    assert config.logging_level == "INFO"
    assert config.retain_posts_for_days == 99


def test_load_missing_config() -> None:
    runtime = Runtime()

    default = runtime.load_config(TEST_CONFIG + "_notthere")

    assert default == _Config()


def test_get_config_returns_cached_copy_of_config() -> None:
    runtime = Runtime()

    config = runtime.get_config()
    config_too = runtime.get_config()

    assert config is config_too


def test_set_logging_tests_nothing_but_here_we_are() -> None:
    # Coverage goes brrr
    runtime = Runtime()

    runtime.set_logging()


def test_connect_database_returns_database_object() -> None:
    runtime = Runtime()

    result = runtime._connect_database()

    assert isinstance(result, Database)
    assert result is runtime._database


def test_get_database_returns_cached_copy_of_database() -> None:
    runtime = Runtime()

    database = runtime.get_database()
    database_too = runtime.get_database()

    assert database is database_too


def test_load_patterns() -> None:
    runtime = Runtime()

    patterns = runtime.load_patterns(TEST_CONFIG)

    assert isinstance(patterns, PatternConfig)
    assert patterns is runtime._patterns


def test_get_patterns_returns_cached_copy() -> None:
    runtime = Runtime()

    patterns = runtime.get_patterns()
    patterns_too = runtime.get_patterns()

    assert patterns is patterns_too


@pytest.mark.parametrize(
    ("file", "logtext", "expected"),
    (
        ("tests/fixture/wypt.toml", "", TEST_PATTERNS),
        ("tests/fixture/wypt.toml.no.there", "Config file not found", set()),
        ("tests/pattern_config_test.py", "Invalid toml format", set()),
        ("pyproject.toml", "section missing from", set()),
    ),
)
def test_load_toml_section(
    caplog: Any,
    file: str,
    logtext: str,
    expected: set[str],
) -> None:
    runtime = Runtime()

    results = runtime._load_toml_section(file, "PATTERNS")
    labels = set(results.keys())

    assert labels == expected
    assert logtext in caplog.text


def test_get_api_returns_cached_copy() -> None:
    runtime = Runtime()

    api = runtime.get_api()
    api_too = runtime.get_api()

    assert api is api_too


def test_set_database() -> None:
    runtime = Runtime()

    runtime.set_database("testing")

    assert runtime._database_file == "testing"
