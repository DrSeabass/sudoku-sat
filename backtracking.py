"""Solve Sudoku by backtracking search, for comparison with the SAT approach in sudoku.py.

Repeatedly pick the empty cell with the fewest legal numbers and try each of
them in turn. When some empty cell has no legal number left, undo the last
choice and try the next one.

    python3 backtracking.py instances/slide.txt
"""

import argparse
import sys

from board import CELLS, NUMBERS, UNITS, Board

# For each cell, the row, column and block it belongs to.
UNITS_OF = {}
for cell in CELLS:
    UNITS_OF[cell] = []
    for unit in UNITS:
        if cell in unit:
            UNITS_OF[cell].append(unit)


def legal_numbers(board, cell):
    """The numbers that can go in cell without repeating one in its row, column or block."""
    used = set()
    for unit in UNITS_OF[cell]:
        for other in unit:
            used.add(board[other])
    legal = []
    for k in NUMBERS:
        if k not in used:
            legal.append(k)
    return legal


def solve(board, stats):
    """Fill the empty cells of board in place. Return True if a solution was found."""
    # Find the empty cell with the fewest legal numbers.
    best_cell = None
    best_numbers = None
    for cell in CELLS:
        if board[cell] is None:
            numbers = legal_numbers(board, cell)
            if best_cell is None or len(numbers) < len(best_numbers):
                best_cell = cell
                best_numbers = numbers
    if best_cell is None:
        return True   # no empty cells left: solved

    for k in best_numbers:
        stats["guesses"] += 1
        board[best_cell] = k
        if solve(board, stats):
            return True
        board[best_cell] = None
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
