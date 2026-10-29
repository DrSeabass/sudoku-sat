"""Solve Sudoku by backtracking search, for comparison with the SAT approach in sudoku.py.

Repeatedly pick the empty cell with the fewest legal numbers and try each of
them in turn. When some empty cell has no legal number left, undo the last
choice and try the next one.

    python3 backtracking.py instances/slide.txt
"""

import argparse
import sys

from board import CELLS, NUMBERS, UNITS, Board

# For each cell, the rows, columns and blocks it belongs to.
UNITS_OF = {cell: [unit for unit in UNITS if cell in unit] for cell in CELLS}


def legal_numbers(board, cell):
    """The numbers that can go in cell without repeating one in its row, column or block."""
    used = {board[other] for unit in UNITS_OF[cell] for other in unit}
    return [k for k in NUMBERS if k not in used]


def solve(board, stats):
    """Fill the empty cells of board in place. Return True if a solution was found."""
    empty = [cell for cell in CELLS if board[cell] is None]
    if not empty:
        return True
    cell = min(empty, key=lambda c: len(legal_numbers(board, c)))
    for k in legal_numbers(board, cell):
        stats["guesses"] += 1
        board[cell] = k
        if solve(board, stats):
            return True
        board[cell] = None
    return False


def main():
    parser = argparse.ArgumentParser(description="Solve Sudoku by backtracking search.")
    parser.add_argument("puzzle")
    args = parser.parse_args()

    try:
        puzzle = Board.from_file(args.puzzle)
    except (OSError, ValueError) as error:
        sys.exit(f"error: {error}")
    print(puzzle)
    print()

    board = Board.from_file(args.puzzle)
    stats = {"guesses": 0}
    if board.has_conflict() or not solve(board, stats):
        print("No solution.")
    else:
        print(board)
    print()
    print(f"Guesses: {stats['guesses']}")


if __name__ == "__main__":
    main()
