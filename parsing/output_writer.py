"""Write a generated maze in the mandatory hexadecimal file format."""

from pathlib import Path
from typing import List

from mazegen.maze_generator import MazeGenerator


def write_output(maze: MazeGenerator,
                 path: List[str]) -> None:
    """Write the wall grid and solution footer to the configured file."""
    lines = ["".join(f"{cell:X}" for cell in row) for row in maze.walls]
    lines += [
        "",
        f"{maze.config.entry[0]},{maze.config.entry[1]}",
        f"{maze.config.exit[0]},{maze.config.exit[1]}",
        "".join(path),
    ]
    Path(maze.config.output_file).write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
