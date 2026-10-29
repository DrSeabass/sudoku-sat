# sudoku-sat

A standalone Sudoku solver that supports backtracking and SAT solving with MiniSat.

## Requirements

- Python 3
- MiniSat (required for the SAT solver)

On Debian or Ubuntu, install MiniSat with:

```sh
./setup.sh
```

## Usage

Run the solver with an input board file:

```sh
python3 sudoku.py path/to/board.txt
```

Each board row contains nine values separated by spaces. Use `_` for empty cells.
Running `python3 sudoku.py` without a file runs the solver on an empty board.

The program prints results from both its internal backtracking solver and the
MiniSat-based SAT solver.
