"""Read and validate the mandatory KEY=VALUE configuration file."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final, Optional, Tuple

Point = Tuple[int, int]


class ConfigError(ValueError):
    """Raised when a configuration file cannot describe a valid maze."""


@dataclass(frozen=True)
class Config:
    """Validated values used by :class:`mazegen.maze.Maze`."""

    width: int
    height: int
    entry: Point
    exit: Point
    output_file: str
    perfect: bool
    seed: Optional[str] = None


REQUIRED: Final[set[str]] = {
    "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
}
ALLOWED: Final[set[str]] = REQUIRED | {"SEED"}


def parse_point(value: str, name: str) -> Point:
    """Convert an ``x,y`` setting into a coordinate."""
    try:
        x_text, y_text = (part.strip() for part in value.split(","))
        return int(x_text), int(y_text)
    except ValueError as error:
        raise ConfigError(f"{name} must be written as x,y") from error


def read_config(filename: str) -> Config:
    """Load *filename*, ignore comments, and return validated settings."""
    values: dict[str, str] = {}
    try:
        lines = Path(filename).read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise ConfigError(
            f"cannot read configuration file: {filename}"
        ) from error
    for line_number, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigError(f"line {line_number}: expected KEY=VALUE")
        key, value = (part.strip() for part in line.split("=", 1))
        key = key.upper()
        if key not in ALLOWED:
            raise ConfigError(f"line {line_number}: unknown key {key}")
        if key in values or not value:
            raise ConfigError(f"line {line_number}: invalid {key}")
        values[key] = value
    missing = REQUIRED - values.keys()
    if missing:
        raise ConfigError("missing: " + ", ".join(sorted(missing)))
    try:
        width, height = int(values["WIDTH"]), int(values["HEIGHT"])
    except ValueError as error:
        raise ConfigError("WIDTH and HEIGHT must be integers") from error
    if width < 1 or height < 1:
        raise ConfigError("WIDTH and HEIGHT must be positive")
    entry = parse_point(values["ENTRY"], "ENTRY")
    exit_ = parse_point(values["EXIT"], "EXIT")
    for name, point in (("ENTRY", entry), ("EXIT", exit_)):
        if not 0 <= point[0] < width or not 0 <= point[1] < height:
            raise ConfigError(f"{name} is outside the maze")
    if entry == exit_:
        raise ConfigError("ENTRY and EXIT must be different")
    perfect = values["PERFECT"].lower()
    if perfect not in {"true", "false"}:
        raise ConfigError("PERFECT must be True or False")
    if perfect == "false" and (width - 1) * (height - 1) < 2:
        raise ConfigError(
            "PERFECT=False requires at least a 2x3 or 3x2 maze "
            "for two independent routes"
        )
    return Config(width, height, entry, exit_, values["OUTPUT_FILE"],
                  perfect == "true", values.get("SEED"))
