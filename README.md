*This project has been created as part of the 42 curriculum by nurya.*

# A-Maze-ing

## Description

`a_maze_ing.py` creates a random, valid maze from a text configuration file,
writes its hexadecimal wall representation, and renders it in the terminal.
It supports perfect mazes and the mandatory playable Pac-Man-like mode.  The
terminal menu regenerates the maze, toggles the shortest path, and cycles wall
colours.

## Instructions

Requires Python 3.10 or later.

```sh
make install
make run
```

The program is also run directly with:

```sh
python3 a_maze_ing.py config.txt
```

Useful checks are `make lint`, `make lint-strict`, `make test`, and
`make build`.  `make build` creates `mazegen-1.0.0-py3-none-any.whl` at the
repository root.  The generated `maze.txt` can be checked with:

```sh
python3 maze_analyzer.py maze.txt --min-loops 2 --max-dead-ends 2
```

## Configuration

The configuration has one `KEY=VALUE` pair per line.  Blank lines and lines
starting with `#` are ignored.  These keys are mandatory:

```text
WIDTH=13              # positive number of cells
HEIGHT=10             # positive number of cells
ENTRY=0,0             # x,y, inside the maze
EXIT=12,9             # x,y, different from ENTRY
OUTPUT_FILE=maze.txt  # output path
PERFECT=False         # True for a perfect maze, False for playable mode
```

`SEED=42` is optional but included in the default configuration.  The same
configuration and seed reproduce the same first generated maze.  Small boards
that cannot hold the visible `42` pattern are generated without it and report
that fact on the terminal.  `PERFECT=False` requires enough room for at least
two independent routes.

## Algorithm and output

The reusable `mazegen.MazeGenerator` uses randomized depth-first search
(recursive backtracking) to build a connected spanning tree.  It was chosen
because it is compact, deterministic with a seed, and naturally produces a
perfect maze.  In normal mode it opens further safe interior walls until there
are at least two independent routes while keeping ordinary dead-ends to at
most two.  It never opens an external wall or creates an open 3x3 area.

Every cell stores closed walls as one hexadecimal digit: North=bit 0,
East=bit 1, South=bit 2, West=bit 3.  The output grid is followed by a blank
line, entry, exit, and the BFS shortest path using `N`, `E`, `S`, and `W`.
Fully closed cells draw the visible `42` pattern.

## Reuse

`mazegen/maze_generator.py` contains the single reusable `MazeGenerator`
class and `GeneratorConfig`.  Build and install the root wheel with `make
build` then `pip install mazegen-1.0.0-py3-none-any.whl`.

```python
from mazegen import GeneratorConfig, MazeGenerator

config = GeneratorConfig(20, 15, (0, 0), (19, 14), False, "42")
maze = MazeGenerator(config)
maze.generate()
print(maze.walls)
print(maze.shortest_path())
```

## Team and project management

This is an individual project.  The author handled design, implementation,
tests, and documentation.  The plan was to first validate parsing and wall
coherence, then implement generation and BFS, then add terminal interaction
and package checks.  Keeping the generator separate from parsing and display
made the algorithm easy to test and package; earlier integration checks would
have made setup issues visible sooner.  Development tools: Python, `pytest`,
`flake8`, `mypy`, `pip`, and `make`.

## Resources and AI use

[](https://docs.python.org/3/library/random.html)
- [Python deque documentation](https://docs.python.org/3/library/collections.html#collections.deque)[](https://en.wikipedia.org/wiki/Depth-first_search)
- 42 A-Maze-ing subject, version 2.3
