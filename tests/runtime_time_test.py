from __future__ import annotations

from wypt.database import Database
from wypt.runtime import _Config
from wypt.runtime import Runtime


def test_load_config() -> None:
    runtime = Runtime()

    config = runtime.load_config("tests/fixture/wypt.toml")

    assert config is runtime._config
    assert config.logging_level == "INFO"
    assert config.retain_posts_for_days == 99


def test_load_missing_config() -> None:
    runtime = Runtime()

    default = runtime.load_config("tests/fixtures/missing.toml")

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


def test_connect_database() -> None:
    runtime = Runtime()

    result = runtime.connect_database()

    assert isinstance(result, Database)
    assert result is runtime._database
