#!/usr/bin/env python3
"""Command-line program for the A-Maze-ing mandatory project."""

from __future__ import annotations

from typing import Final, List

from display.ascii_display import render_maze
from mazegen import MazeGenerator
from parsing.config_parser import ConfigError, read_config
from parsing.output_writer import write_output

MENU: Final[str] = (
    "\n=== A-Maze-ing ===\n"
    "1. Re-generate a new maze\n"
    "2. Show / hide the shortest path\n"
    "3. Change wall colour\n"
    "4. Quit\n"
)


def clear_screen() -> None:
    """Clear an ANSI-compatible terminal before drawing the next maze."""
    print("\033[2J\033[H", end="")


def show(maze: MazeGenerator, path: List[str], visible: bool,
         colour: str) -> None:
    """Draw the current maze and a small legend."""
    clear_screen()
    print(render_maze(maze, path if visible else [], colour))
    if maze.pattern_omitted:
        print("Error: maze is too small to draw the 42 pattern; omitted.")
    print("\nE = entry, X = exit, # = closed 42 cells, * = shortest path")


def interactive(maze: MazeGenerator) -> None:
    """Run the four required terminal interactions until the user quits."""
    path = maze.shortest_path()
    visible = True
    colours = ["36", "33", "35", "32"]
    colour_index = 0
    while True:
        show(maze, path, visible, colours[colour_index])
        try:
            choice = input(MENU + "Choice (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return
        if choice == "1":
            maze.generate()
            path = maze.shortest_path()
            write_output(maze, path)
        elif choice == "2":
            visible = not visible
        elif choice == "3":
            colour_index = (colour_index + 1) % len(colours)
        elif choice == "4":
            return
        else:
            print("Please choose 1, 2, 3 or 4.")


def main() -> int:
    """Read one config file, create the first maze, then open the menu."""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return 1
    try:
        config = read_config(sys.argv[1])
        maze = MazeGenerator(config)
        maze.generate()
        path = maze.shortest_path()
        write_output(maze, path)
        interactive(maze)
    except (OSError, ConfigError, ValueError) as error:
        print(f"Error: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
