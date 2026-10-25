"""Checks for the reusable maze generator."""

import pytest

from parsing.config_parser import Config
from mazegen import MazeGenerator


def test_generator_connects_entry_and_exit() -> None:
    """A generated perfect maze has a solution from entry to exit."""
    config = Config(13, 10, (0, 0), (12, 9), "unused.txt", True, "42")
    maze = MazeGenerator(config)
    maze.generate()

    assert maze.shortest_path()


def test_seed_reproduces_the_same_maze() -> None:
    """The same seed and configuration produce the same wall grid."""
    config = Config(13, 10, (0, 0), (12, 9), "unused.txt", False, "42")
    first = MazeGenerator(config)
    second = MazeGenerator(config)
    first.generate()
    second.generate()

    assert first.walls == second.walls


def test_perfect_maze_has_no_cycles() -> None:
    """A perfect maze has exactly one fewer open edge than corridor cells."""
    config = Config(13, 10, (0, 0), (12, 9), "unused.txt", True, "42")
    maze = MazeGenerator(config)
    maze.generate()

    corridor_count = maze.width * maze.height - len(maze.logo)
    edge_count = sum(
        (x + 1 < maze.width and not walls & 2)
        + (y + 1 < maze.height and not walls & 4)
        for y, row in enumerate(maze.walls)
        for x, walls in enumerate(row)
    )

    assert edge_count == corridor_count - 1


def test_playable_maze_has_multiple_routes() -> None:
    """The default mode opens enough walls to produce several cycles."""
    config = Config(13, 10, (0, 0), (12, 9), "unused.txt", False, "42")
    maze = MazeGenerator(config)
    maze.generate()

    corridor_count = maze.width * maze.height - len(maze.logo)
    edge_count = sum(
        (x + 1 < maze.width and not walls & 2)
        + (y + 1 < maze.height and not walls & 4)
        for y, row in enumerate(maze.walls)
        for x, walls in enumerate(row)
    )

    assert edge_count - corridor_count + 1 >= 2


def test_playable_maze_obeys_board_constraints() -> None:
    """Normal mode preserves borders, avoids 3x3 rooms and rare dead ends."""
    config = Config(13, 10, (0, 0), (12, 9), "unused.txt", False, "42")
    maze = MazeGenerator(config)
    maze.generate()

    assert all(wall & 1 for wall in maze.walls[0])
    assert all(wall & 4 for wall in maze.walls[-1])
    assert all(row[0] & 8 and row[-1] & 2 for row in maze.walls)
    real_dead_ends = [
        (x, y) for y in range(maze.height) for x in range(maze.width)
        if (x, y) not in maze.logo
        and sum(1 for _ in maze.passage_neighbours((x, y))) == 1
        and maze._is_real_dead_end((x, y))
    ]
    assert len(real_dead_ends) <= 2
    for y in range(maze.height - 2):
        for x in range(maze.width - 2):
            edges = [
                not (maze.walls[y + row][x + column] & 2)
                for row in range(3) for column in range(2)
            ] + [
                not (maze.walls[y + row][x + column] & 4)
                for row in range(2) for column in range(3)
            ]
            assert not all(edges)


def test_small_maze_omits_logo_to_keep_corners_open() -> None:
    """A maze too small for a bordered logo leaves every cell available."""
    config = Config(8, 8, (0, 0), (7, 7), "unused.txt", False, "42")
    maze = MazeGenerator(config)
    maze.generate()

    assert maze.pattern_omitted
    assert not maze.logo


def test_generator_rejects_impossible_playable_dimensions() -> None:
    """The reusable package rejects a board that cannot have two loops."""
    config = Config(2, 2, (0, 0), (1, 1), "unused.txt", False, "42")

    with pytest.raises(ValueError, match="two independent routes"):
        MazeGenerator(config)
