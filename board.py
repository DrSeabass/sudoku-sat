"""Reading, printing and checking Sudoku boards.

Rows, columns and numbers all run from 1 to 9, as in the lecture:
cell (i, j) is row i, column j.
"""

N = 9                       # the grid is N x N
BLOCK = 3                   # made of BLOCK x BLOCK blocks
NUMBERS = range(1, N + 1)   # 1, ..., 9
BLANKS = "_."               # characters that mark an empty cell


def all_cells():
    """All 81 cells (i, j)."""
    cells = []
    for i in NUMBERS:
        for j in NUMBERS:
            cells.append((i, j))
    return cells


def all_units():
    """The 27 groups of cells that must each contain every number exactly once:
    9 rows, 9 columns and 9 blocks."""
    units = []
    for i in NUMBERS:
        row = []
        for j in NUMBERS:
            row.append((i, j))
        units.append(row)
    for j in NUMBERS:
        column = []
        for i in NUMBERS:
            column.append((i, j))
        units.append(column)
    for bi in range(BLOCK):
        for bj in range(BLOCK):
            block = []
            for di in range(1, BLOCK + 1):
                for dj in range(1, BLOCK + 1):
                    block.append((BLOCK * bi + di, BLOCK * bj + dj))
            units.append(block)
    return units


CELLS = all_cells()
UNITS = all_units()


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
        clues = []
        for cell in sorted(self.cells):
            i, j = cell
            clues.append((i, j, self.cells[cell]))
        return clues

    def has_conflict(self):
        """True if some row, column or block contains a number twice."""
        for unit in UNITS:
            seen = set()
            for cell in unit:
                number = self[cell]
                if number is None:
                    continue
                if number in seen:
                    return True
                seen.add(number)
        return False

    def is_solution_of(self, puzzle):
        """True if this board is a complete, correct solution that keeps puzzle's clues."""
        for cell in CELLS:
            if self[cell] is None:
                return False
        for i, j, k in puzzle.clues():
            if self[i, j] != k:
                return False
        return not self.has_conflict()

    def __str__(self):
        lines = []
        for i in NUMBERS:
            line = ""
            for j in NUMBERS:
                number = self[i, j]
                if number is None:
                    line += "_"
                else:
                    line += str(number)
                if j == N:
                    pass
                elif j % BLOCK == 0:
                    line += " | "
                else:
                    line += " "
            lines.append(line)
            if i % BLOCK == 0 and i < N:
                lines.append("------+-------+------")
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
                line = line.replace(" ", "").strip()
                if line and not line.startswith("#"):
                    rows.append(line)
        if len(rows) != N:
            raise ValueError(f"{path}: expected {N} rows, found {len(rows)}")

        board = Board()
        for i in NUMBERS:
            row = rows[i - 1]
            if len(row) != N:
                raise ValueError(f"{path}: row {i} has {len(row)} cells, expected {N}")
            for j in NUMBERS:
                char = row[j - 1]
                if char in BLANKS:
                    continue
                if not char.isdigit() or int(char) not in NUMBERS:
                    raise ValueError(f"{path}: row {i}, column {j}: unexpected {char!r}")
                board[i, j] = int(char)
        return board
