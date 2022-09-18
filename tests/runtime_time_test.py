from __future__ import annotations

from wypt.runtime import _Config
from wypt.runtime import Runtime


def test_default_config_on_init() -> None:
    runtime = Runtime()

    assert _Config() == runtime.config


def test_load_config() -> None:
    runtime = Runtime()

    config = runtime.load_config("tests/fixture/wypt.toml")

    assert config.logging_level == "INFO"
    assert config.retain_posts_for_days == 99


def test_load_missing_config() -> None:
    runtime = Runtime()

    default = runtime.load_config("tests/fixtures/missing.toml")

    assert default == _Config()


def test_set_logging() -> None:
    # Coverage goes brrr
    runtime = Runtime()

    runtime.set_logging()
