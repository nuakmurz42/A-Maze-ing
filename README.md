*This project has been created as part of the 42 curriculum by nuakmurz, jsingh.*

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

`Makefile` is a small command shortcut: it does not compile Python code.  It
keeps the installation, checks, and package-build commands consistent.

| Command | What it does |
| --- | --- |
| `make install` | Creates `.venv` with Python 3.12, upgrades `pip`, installs this project in editable mode, then installs the development tools from `requirements-dev.txt`. Run this once first. |
| `make run` | Starts `a_maze_ing.py` with the default `config.txt`. |
| `make test` | Runs the automated tests in `tests/` using the virtual environment. |
| `make lint` | Runs `flake8` for formatting/style issues, then `mypy` with the project's typed-check options. A non-zero result means a code-quality or type-checking error must be fixed. |
| `make lint-strict` | Runs `flake8` again and then `mypy --strict`, the strongest required type check. |
| `make build` | Builds an installable wheel from `pyproject.toml` and places `mazegen-1.0.0-py3-none-any.whl` at the repository root. It requires `make install` first. |
| `make check` | Runs lint, strict lint, tests, and the wheel build in sequence. |
| `make clean` | Removes generated caches, build artefacts, test caches, and the generated `maze.txt`; it does not remove source files. |

For a clean evaluation-style package check, run `make install`, `make check`,
then install the generated wheel in a second virtual environment before
running the application again.

### Rebuild and verify the reusable wheel

The following procedure verifies the reusable `mazegen` package independently
of the development environment.  It is the procedure to demonstrate during
the reusable-module part of the evaluation:

```sh
# 1. Build a fresh wheel from the source and pyproject.toml.
make build

# 2. Create a separate, clean environment for the installed package.
python3.12 -m venv /tmp/mazegen-wheel-venv
source /tmp/mazegen-wheel-venv/bin/activate

# 3. Install exactly the wheel that was just built.
python -m pip install --force-reinstall "$(pwd)/mazegen-1.0.0-py3-none-any.whl"

# 4. Run the installed application with the repository configuration.
a-maze-ing "$(pwd)/config.txt"

deactivate
```

`make build` uses the build information in `pyproject.toml` and creates the
wheel at the repository root.  `LICENSE.md` and `README.md` are kept at the
repository root; the package metadata declares `LICENSE.md` as its license
file.  Do not copy either file manually into the virtual environment: the
wheel installation handles the package metadata.

### Code-quality checks

Run these commands after `make install`:

```sh
make lint
make lint-strict
```

`make lint` verifies both Python style (`flake8`) and type annotations
(`mypy`).  `make lint-strict` repeats the style check and requires the code to
pass `mypy --strict`.  The project must finish both commands with exit status
zero before delivery.  `make check` is the one-command equivalent for the
full delivery check: linting, strict type checking, tests, and wheel build.

The program is also run directly with:

```sh
python3 a_maze_ing.py config.txt
```

The generated `maze.txt` can be checked with:

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

config = GeneratorConfig(
    width=20,
    height=15,
    entry=(0, 0),
    exit=(19, 14),
    perfect=False,
    seed="42",
)
maze = MazeGenerator(config)
maze.generate()
walls = maze.walls                 # Generated maze structure
shortest_path = maze.shortest_path()  # One shortest N/E/S/W solution
print(walls)
print(shortest_path)
```

## Team and project management

### Roles

- **nuakmurz**: core maze-generator design, package integration, and terminal
  application implementation.
- **jsingh**: configuration parsing and output writing implementation
  (`parsing/config_parser.py` and `parsing/output_writer.py`), automated test
  implementation, documentation review, and final repository checks.

Both members reviewed the mandatory requirements and the final behaviour.

### Planning and retrospective

The original plan was to validate parsing and wall coherence first, then
implement generation and BFS, and finally add terminal interaction and
package checks.  Keeping the generator separate from parsing and display made
the algorithm easy to test and package.  The separation of concerns and
automated checks worked well; running packaging and terminal checks earlier
would have surfaced environment and terminal-size issues sooner.

Development tools: Python, `pytest`, `flake8`, `mypy`, `pip`, `venv`, `make`,
and Git/GitHub.

## Resources and AI use
AI assistance was used to review the mandatory checklist, clarify
documentation and test cases, and propose improvements README.
