"""Coloured ASCII terminal rendering for a maze."""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

from mazegen.maze_generator import EAST, NORTH, SOUTH, WEST, MazeGenerator

Point = Tuple[int, int]
RESET = "\033[0m"
ENTRY_COLOUR = "\033[95m"
EXIT_COLOUR = "\033[91m"
PATH_COLOUR = "\033[96m"
LOGO_COLOUR = "\033[97m"


def colour(text: str, code: str) -> str:
    """Wrap *text* in one ANSI foreground-colour escape sequence."""
    return f"\033[{code}m{text}{RESET}"


def solution_cells(maze: MazeGenerator, path: List[str]) -> Set[Point]:
    """Turn N/E/S/W route letters into the cells visited by the route."""
    x, y = maze.config.entry
    cells = {(x, y)}
    offsets: Dict[str, Point] = {
        "N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)
    }
    for letter in path:
        dx, dy = offsets[letter]
        x, y = x + dx, y + dy
        cells.add((x, y))
    return cells


def cell_symbol(maze: MazeGenerator, point: Point, path: Set[Point]) -> str:
    """Return the coloured character displayed inside one maze cell."""
    if point in maze.logo:
        return f"{LOGO_COLOUR}#{RESET}"
    if point == maze.config.entry:
        return f"{ENTRY_COLOUR}E{RESET}"
    if point == maze.config.exit:
        return f"{EXIT_COLOUR}X{RESET}"
    if point in path:
        return f"{PATH_COLOUR}*{RESET}"
    return " "


def render_maze(maze: MazeGenerator, path: List[str],
                wall_code: str = "36") -> str:
    """Return a maze with coloured walls and coloured important cells.

    ``wall_code`` is an ANSI foreground colour chosen by the menu.  Path,
    entry, exit and the closed ``42`` cells intentionally keep their own
    colours so they remain recognisable after a wall-colour change.
    """
    route = solution_cells(maze, path)
    lines: List[str] = []
    for y in range(maze.height):
        top: List[str] = []
        middle: List[str] = []
        for x in range(maze.width):
            walls = maze.walls[y][x]
            top.append(colour("+---" if walls & NORTH else "+   ", wall_code))
            middle.append(colour("|" if walls & WEST else " ", wall_code))
            middle.append(f" {cell_symbol(maze, (x, y), route)} ")
        top.append(colour("+", wall_code))
        middle.append(
            colour("|" if maze.walls[y][-1] & EAST else " ", wall_code)
        )
        lines.extend(("".join(top), "".join(middle)))
    bottom = "".join(
        colour("+---" if walls & SOUTH else "+   ", wall_code)
        for walls in maze.walls[-1]
    )
    lines.append(bottom + colour("+", wall_code))
    return "\n".join(lines)
