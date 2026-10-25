"""Reusable DFS maze generation and shortest-path solving.

Basic usage::

    from mazegen import GeneratorConfig, MazeGenerator

    config = GeneratorConfig(width=20, height=15, entry=(0, 0),
                             exit=(19, 14), seed="42")
    maze = MazeGenerator(config)
    maze.generate()
    walls = maze.walls
    solution = maze.shortest_path()

``GeneratorConfig`` accepts custom dimensions, endpoints, perfect-mode and
seed values.  ``walls`` is the generated wall structure; ``solution`` is a
list containing the N/E/S/W moves of one shortest solution.
"""
from collections import deque
from dataclasses import dataclass
import random
from typing import Iterator, List, Optional, Protocol, Set, Tuple

NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8
DIRECTIONS = (("N", 0, -1, NORTH, SOUTH), ("E", 1, 0, EAST, WEST),
              ("S", 0, 1, SOUTH, NORTH), ("W", -1, 0, WEST, EAST))


Point = Tuple[int, int]
Direction = Tuple[str, int, int, int, int]


class MazeConfig(Protocol):
    """Configuration values required by :class:`MazeGenerator`."""

    @property
    def width(self) -> int:
        """Return the maze width in cells."""

    @property
    def height(self) -> int:
        """Return the maze height in cells."""

    @property
    def entry(self) -> Point:
        """Return the entry cell."""

    @property
    def exit(self) -> Point:
        """Return the exit cell."""

    @property
    def output_file(self) -> str:
        """Return the path where the generated maze is written."""

    @property
    def perfect(self) -> bool:
        """Return whether generation must create a perfect maze."""

    @property
    def seed(self) -> Optional[str]:
        """Return the optional random seed."""


@dataclass(frozen=True)
class GeneratorConfig:
    """Standalone configuration accepted by :class:`MazeGenerator`.

    Args:
        width: Number of cells along the horizontal axis.
        height: Number of cells along the vertical axis.
        entry: Starting ``(x, y)`` cell.
        exit: Destination ``(x, y)`` cell.
        perfect: Whether to generate a maze with no cycles.
        seed: Optional seed used to reproduce a generated maze.
        output_file: Optional application-level output filename.
    """

    width: int
    height: int
    entry: Point
    exit: Point
    perfect: bool = False
    seed: Optional[str] = None
    output_file: str = "maze.txt"


class MazeGenerator:
    """Create a maze, expose its wall grid, and solve its shortest path."""

    def __init__(self, config: MazeConfig) -> None:
        """Store configuration and initialise every wall as closed."""
        self.config = config
        self.width, self.height = config.width, config.height
        if self.width < 1 or self.height < 1:
            raise ValueError("width and height must be positive")
        if not self.inside(config.entry) or not self.inside(config.exit):
            raise ValueError("entry and exit must be inside the maze")
        if config.entry == config.exit:
            raise ValueError("entry and exit must be different")
        if not config.perfect and (self.width - 1) * (self.height - 1) < 2:
            raise ValueError(
                "PERFECT=False requires at least a 2x3 or 3x2 maze "
                "for two independent routes"
            )
        self.random = random.Random(config.seed)
        # The seven-by-seven logo needs a one-cell open border.
        self.pattern_omitted = self.width < 9 or self.height < 9
        self.logo = self._logo_cells()
        if config.entry in self.logo or config.exit in self.logo:
            raise ValueError("ENTRY and EXIT cannot be inside the 42 pattern")
        self.walls = [[15] * self.width for _ in range(self.height)]

    def _logo_cells(self) -> Set[Point]:
        """Return fully closed cells that form the mandatory ``42`` logo."""
        # 4 on the left; correctly shaped 2 on the right.
        drawing = ("# # ###", "# #   #", "### ###", "  # #  ", "  # #  ",
                   "  # #  ", "  # ###")
        if self.pattern_omitted:
            return set()
        left, top = (self.width - 7) // 2, (self.height - 7) // 2
        return {(left + x, top + y) for y, row in enumerate(drawing)
                for x, char in enumerate(row) if char == "#"}

    def inside(self, point: Point) -> bool:
        """Return whether *point* is inside the maze boundaries."""
        x, y = point
        return 0 <= x < self.width and 0 <= y < self.height

    def neighbours(self, point: Point) -> Iterator[Tuple[Point, int, int]]:
        """Yield non-logo neighbours with their wall bits and opposite bits."""
        x, y = point
        for _letter, dx, dy, side, other_side in DIRECTIONS:
            other = x + dx, y + dy
            if self.inside(other) and other not in self.logo:
                yield other, side, other_side

    def _open(self, point: Point, other: Point, side: int,
              other_side: int) -> None:
        """Open the shared wall between two adjacent cells on both sides."""
        x, y = point
        ox, oy = other
        self.walls[y][x] &= ~side
        self.walls[oy][ox] &= ~other_side

    def generate(self) -> None:
        """Generate a maze; repeated calls advance the seeded sequence."""
        self.walls = [[15] * self.width for _ in range(self.height)]
        corridors = {
            (x, y) for y in range(self.height) for x in range(self.width)
        } - self.logo
        visited, stack = {self.config.entry}, [self.config.entry]
        while stack:
            cell = stack[-1]
            choices = [item for item in self.neighbours(cell)
                       if item[0] not in visited]
            if not choices:
                stack.pop()
                continue
            other, side, other_side = self.random.choice(choices)
            self._open(cell, other, side, other_side)
            visited.add(other)
            stack.append(other)
        if visited != corridors:
            raise ValueError(
                "the 42 pattern splits this maze; use a larger size"
            )
        if not self.config.perfect:
            self._add_loops()

    def _add_loops(self) -> None:
        """Open safe interior walls to create a connected playable board."""
        candidates: List[Tuple[Point, Point, int, int]] = []
        for y in range(self.height):
            for x in range(self.width):
                point = x, y
                if point not in self.logo:
                    for other, side, opposite in self.neighbours(point):
                        if point < other and self.walls[y][x] & side:
                            candidates.append((point, other, side, opposite))
        self.random.shuffle(candidates)
        # Two openings are the mandatory minimum for two independent routes.
        # Further openings are made only to keep ordinary dead-ends rare.
        for point, other, side, opposite in candidates[:2]:
            if not self._would_make_open_3_by_3(point, other):
                self._open(point, other, side, opposite)
        # Keep the ordinary mode playable without turning it into the
        # no-dead-end bonus: at most two ordinary dead-ends are tolerated.
        while True:
            dead_ends = [
                (x, y) for y in range(self.height) for x in range(self.width)
                if (x, y) not in self.logo
                and sum(1 for _ in self.passage_neighbours((x, y))) == 1
                and self._is_real_dead_end((x, y))
            ]
            if len(dead_ends) <= 2:
                return
            self.random.shuffle(dead_ends)
            opened = False
            for point in dead_ends:
                x, y = point
                closed = [
                    item for item in self.neighbours(point)
                    if self.walls[y][x] & item[1]
                    and not self._would_make_open_3_by_3(point, item[0])
                ]
                if closed:
                    other, side, opposite = self.random.choice(closed)
                    self._open(point, other, side, opposite)
                    opened = True
                    break
            if not opened:
                return

    def _is_real_dead_end(self, point: Point) -> bool:
        """Return whether a dead-end can be opened toward a corridor cell."""
        x, y = point
        return any(
            self.walls[y][x] & side
            for other, side, _opposite in self.neighbours(point)
            if other not in self.logo
        )

    def _would_make_open_3_by_3(self, first: Point, second: Point) -> bool:
        """Return whether this opening would make a fully open 3x3 area."""
        changed = frozenset((first, second))

        def open_after(left: Point, right: Point) -> bool:
            """Return whether cells share an open wall after this change."""
            if frozenset((left, right)) == changed:
                return True
            x, y = left
            ox, oy = right
            if x + 1 == ox:
                return not (self.walls[y][x] & EAST)
            if y + 1 == oy:
                return not (self.walls[y][x] & SOUTH)
            return not (self.walls[oy][ox] & (WEST if ox + 1 == x else NORTH))

        top_start = max(0, min(first[1], second[1]) - 2)
        left_start = max(0, min(first[0], second[0]) - 2)
        for top in range(top_start, self.height - 2):
            for left in range(left_start, self.width - 2):
                cells = [
                    (left + x, top + y) for y in range(3) for x in range(3)
                ]
                if first not in cells and second not in cells:
                    continue
                horizontal = all(
                    open_after((left + x, top + y),
                               (left + x + 1, top + y))
                    for y in range(3) for x in range(2)
                )
                vertical = all(
                    open_after((left + x, top + y),
                               (left + x, top + y + 1))
                    for y in range(2) for x in range(3)
                )
                if horizontal and vertical:
                    return True
        return False

    def passage_neighbours(self, point: Point) -> Iterator[Tuple[Point, str]]:
        """Yield reachable neighbours paired with their N/E/S/W direction."""
        x, y = point
        for letter, dx, dy, side, opposite in DIRECTIONS:
            other = x + dx, y + dy
            if (self.inside(other) and not (self.walls[y][x] & side)
                    and not (self.walls[other[1]][other[0]] & opposite)):
                yield other, letter

    def shortest_path(self) -> List[str]:
        """Return the shortest entry-to-exit route as direction letters."""
        start: Point = self.config.entry
        finish: Point = self.config.exit
        queue: deque[Point] = deque([start])
        parent: dict[Point, Tuple[Point, str]] = {}
        while queue:
            current = queue.popleft()
            if current == finish:
                break
            for other, letter in self.passage_neighbours(current):
                if other not in parent:
                    parent[other] = current, letter
                    queue.append(other)
        if finish not in parent:
            raise ValueError("EXIT cannot be reached")
        result: List[str] = []
        current = finish
        while current != start:
            current, letter = parent[current]
            result.append(letter)
        return list(reversed(result))
