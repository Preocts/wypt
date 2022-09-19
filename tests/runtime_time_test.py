from __future__ import annotations

from wypt.database import Database
from wypt.pattern_config import PatternConfig
from wypt.runtime import _Config
from wypt.runtime import Runtime

TEST_CONFIG = "tests/fixture/wypt.toml"


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

    result = runtime.connect_database()

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
