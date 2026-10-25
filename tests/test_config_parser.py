"""Checks for the configuration parser."""

from pathlib import Path

import pytest

from parsing.config_parser import ConfigError, read_config


def test_read_config_accepts_required_settings(tmp_path: Path) -> None:
    """A complete configuration returns a validated object."""
    config_file = tmp_path / "config.txt"
    config_file.write_text(
        "WIDTH=13\nHEIGHT=10\nENTRY=0,0\nEXIT=12,9\n"
        "OUTPUT_FILE=maze.txt\nPERFECT=False\nSEED=42\n",
        encoding="utf-8",
    )

    config = read_config(str(config_file))

    assert (config.width, config.height, config.seed) == (13, 10, "42")


def test_read_config_rejects_equal_entry_and_exit(tmp_path: Path) -> None:
    """The entry and exit must be distinct cells."""
    config_file = tmp_path / "bad.txt"
    config_file.write_text(
        "WIDTH=2\nHEIGHT=2\nENTRY=0,0\nEXIT=0,0\n"
        "OUTPUT_FILE=maze.txt\nPERFECT=True\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="different"):
        read_config(str(config_file))


def test_read_config_ignores_comments_and_rejects_bad_boolean(
        tmp_path: Path) -> None:
    """Comments are ignored while invalid mandatory values are rejected."""
    config_file = tmp_path / "bad-boolean.txt"
    config_file.write_text(
        "# A comment\nWIDTH=2\nHEIGHT=2\nENTRY=0,0\nEXIT=1,1\n"
        "OUTPUT_FILE=maze.txt\nPERFECT=perhaps\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="True or False"):
        read_config(str(config_file))


def test_read_config_rejects_out_of_bounds_entry(tmp_path: Path) -> None:
    """Coordinates outside the configured dimensions cannot describe a maze."""
    config_file = tmp_path / "outside.txt"
    config_file.write_text(
        "WIDTH=2\nHEIGHT=2\nENTRY=2,0\nEXIT=1,1\n"
        "OUTPUT_FILE=maze.txt\nPERFECT=True\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="outside"):
        read_config(str(config_file))


def test_read_config_rejects_impossible_playable_dimensions(
        tmp_path: Path) -> None:
    """A playable board needs room for at least two independent routes."""
    config_file = tmp_path / "too-small.txt"
    config_file.write_text(
        "WIDTH=2\nHEIGHT=2\nENTRY=0,0\nEXIT=1,1\n"
        "OUTPUT_FILE=maze.txt\nPERFECT=False\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="two independent routes"):
        read_config(str(config_file))
