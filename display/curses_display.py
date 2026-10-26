"""Full-screen terminal interface for the interactive maze display."""

from __future__ import annotations

import curses
import re
from typing import Callable, List

from mazegen import MazeGenerator

from .ascii_display import render_maze

ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")
COLOURS = (curses.COLOR_CYAN, curses.COLOR_YELLOW, curses.COLOR_MAGENTA,
           curses.COLOR_GREEN)
ENTRY_PAIR = 5
EXIT_PAIR = 6
PATH_PAIR = 7
LOGO_PAIR = 8


def run(maze: MazeGenerator,
        write_output: Callable[[MazeGenerator, List[str]], None]) -> None:
    """Run a redraw-in-place interface and restore the terminal on exit."""
    curses.wrapper(_main, maze, write_output)


def _main(screen: curses.window, maze: MazeGenerator,
          write_output: Callable[[MazeGenerator, List[str]], None]) -> None:
    """Handle drawing and key input inside curses' alternate screen buffer."""
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    for index, colour in enumerate(COLOURS, start=1):
        curses.init_pair(index, colour, -1)
    curses.init_pair(ENTRY_PAIR, curses.COLOR_MAGENTA, -1)
    curses.init_pair(EXIT_PAIR, curses.COLOR_RED, -1)
    curses.init_pair(PATH_PAIR, curses.COLOR_CYAN, -1)
    curses.init_pair(LOGO_PAIR, curses.COLOR_WHITE, -1)

    path = maze.shortest_path()
    visible = True
    colour_index = 0
    while True:
        _draw(screen, maze, path, visible, colour_index)
        key = screen.getch()
        if key in (ord("1"), ord("r"), ord("R")):
            maze.generate()
            path = maze.shortest_path()
            write_output(maze, path)
        elif key in (ord("2"), ord("p"), ord("P")):
            visible = not visible
        elif key in (ord("3"), ord("c"), ord("C")):
            colour_index = (colour_index + 1) % len(COLOURS)
        elif key in (ord("4"), ord("q"), ord("Q"), 27):
            return


def _draw(screen: curses.window, maze: MazeGenerator, path: List[str],
          visible: bool, colour_index: int) -> None:
    """Erase the old frame and redraw the maze in the same screen area."""
    screen.erase()
    height, width = screen.getmaxyx()
    lines = ANSI_ESCAPE.sub("", render_maze(maze, path if visible else []))
    maze_lines = lines.splitlines()
    menu = (
        "",
        "=== A-Maze-ing ===",
        "1. Re-generate a new maze",
        "2. Show / hide the shortest path",
        "3. Change wall colour",
        "4. Quit",
        "Choice (1-4):",
    )
    required_rows = len(maze_lines) + len(menu)
    too_narrow = any(len(line) >= width for line in maze_lines)
    if required_rows > height or too_narrow:
        message = "Terminal is too small; enlarge it, then press any key."
        screen.addnstr(0, 0, message, max(width - 1, 0))
        screen.refresh()
        return

    colour = curses.color_pair(colour_index + 1)
    for row, line in enumerate(maze_lines):
        _draw_coloured_line(screen, row, line, colour)
    if maze.pattern_omitted:
        screen.addstr(
            len(maze_lines), 0,
            "Error: maze is too small to draw the 42 pattern; omitted."
        )
    menu_start = len(maze_lines) + (2 if maze.pattern_omitted else 1)
    for offset, line in enumerate(menu):
        screen.addstr(menu_start + offset, 0, line)
    screen.refresh()


def _draw_coloured_line(screen: curses.window, row: int, line: str,
                        wall_colour: int) -> None:
    """Draw maze symbols with fixed colours over the chosen wall colour."""
    colours = {
        "E": curses.color_pair(ENTRY_PAIR),
        "X": curses.color_pair(EXIT_PAIR),
        "*": curses.color_pair(PATH_PAIR),
        "#": curses.color_pair(LOGO_PAIR),
    }
    for column, character in enumerate(line):
        attribute = colours.get(character, wall_colour)
        screen.addch(row, column, character, attribute)
