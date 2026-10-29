"""Reading, printing and checking Sudoku boards.

Rows, columns and numbers all run from 1 to 9, as in the lecture:
cell (i, j) is row i, column j.
"""

N = 9                       # the grid is N x N
BLOCK = 3                   # made of BLOCK x BLOCK blocks
NUMBERS = range(1, N + 1)   # 1, ..., 9
BLANKS = "_."               # characters that mark an empty cell

CELLS = [(i, j) for i in NUMBERS for j in NUMBERS]

# The 27 groups of cells that must each contain every number exactly once.
ROWS = [[(i, j) for j in NUMBERS] for i in NUMBERS]
COLUMNS = [[(i, j) for i in NUMBERS] for j in NUMBERS]
BLOCKS = [[(BLOCK * bi + di, BLOCK * bj + dj)
           for di in range(1, BLOCK + 1) for dj in range(1, BLOCK + 1)]
          for bi in range(BLOCK) for bj in range(BLOCK)]
UNITS = ROWS + COLUMNS + BLOCKS


class Board:
    """A Sudoku grid. board[i, j] is the number in cell (i, j), or None if empty."""

    def __init__(self):
        self.cells = {}

    def __getitem__(self, cell):
        return self.cells.get(cell)

    def __setitem__(self, cell, number):
        if number is None:
            self.cells.pop(cell, None)
        else:
            self.cells[cell] = number

    def clues(self):
        """The filled cells, as (i, j, k): cell (i, j) contains k."""
        return [(i, j, k) for (i, j), k in sorted(self.cells.items())]

    def has_conflict(self):
        """True if some row, column or block contains a number twice."""
        for unit in UNITS:
            numbers = [self[cell] for cell in unit if self[cell] is not None]
            if len(numbers) != len(set(numbers)):
                return True
        return False

    def is_solution_of(self, puzzle):
        """True if this board is a complete, correct solution that keeps puzzle's clues."""
        complete = all(self[cell] is not None for cell in CELLS)
        keeps_clues = all(self[i, j] == k for i, j, k in puzzle.clues())
        return complete and keeps_clues and not self.has_conflict()

    def __str__(self):
        lines = []
        for i in NUMBERS:
            groups = [" ".join(str(self[i, j] or "_") for j in range(start, start + BLOCK))
                      for start in range(1, N + 1, BLOCK)]
            lines.append(" | ".join(groups))
            if i % BLOCK == 0 and i < N:
                lines.append("-+-".join(["-" * (2 * BLOCK - 1)] * (N // BLOCK)))
        return "\n".join(lines)

    @staticmethod
    def from_file(path):
        """Read a board: 9 rows of 9 cells, digits for clues and _ or . for blanks.

        Spaces between cells are optional; blank lines and lines starting
        with # are ignored.
        """
        rows = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = "".join(line.split())
                if line and not line.startswith("#"):
                    rows.append(line)
        if len(rows) != N:
            raise ValueError(f"{path}: expected {N} rows, found {len(rows)}")

        board = Board()
        for i, row in zip(NUMBERS, rows):
            if len(row) != N:
                raise ValueError(f"{path}: row {i} has {len(row)} cells, expected {N}")
            for j, char in zip(NUMBERS, row):
                if char in BLANKS:
                    continue
                if not char.isdigit() or int(char) not in NUMBERS:
                    raise ValueError(f"{path}: row {i}, column {j}: unexpected {char!r}")
                board[i, j] = int(char)
        return board
