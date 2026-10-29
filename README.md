# sudoku-sat

Solve Sudoku by turning it into a propositional logic formula and handing that
formula to a SAT solver (MiniSat). The encoding is the one from the logic
course lectures.

## Requirements

- Python 3
- MiniSat

Install MiniSat on Debian or Ubuntu with `./setup.sh` (runs
`sudo apt-get install minisat`), or on macOS with `brew install minisat`.

## The idea

Introduce one propositional variable for every cell and number:

> v<sub>i,j,k</sub> is true &iff; cell (i, j) contains the number k

for rows i, columns j and numbers k from 1 to 9: 729 variables in total.
The rules of Sudoku become a formula
&Phi; = &phi;<sub>1</sub> &and; &phi;<sub>2</sub> &and; &phi;<sub>3</sub> &and; &phi;<sub>4</sub> &and; &phi;<sub>5</sub> &and; &phi;<sub>s</sub>:

| Part | Says | Clauses |
|---|---|---|
| &phi;<sub>1</sub> | every cell has at least one number | 81 |
| &phi;<sub>2</sub> | every cell has at most one number | 2916 |
| &phi;<sub>3</sub> | every number occurs in every row | 81 |
| &phi;<sub>4</sub> | every number occurs in every column | 81 |
| &phi;<sub>5</sub> | every number occurs in every 3&times;3 block | 81 |
| &phi;<sub>s</sub> | the clues of this puzzle | one per clue |

A satisfying interpretation of &Phi; is exactly a solved grid. Each part is a
function of the same name in `sudoku.py`.

## Usage

The whole pipeline in one command:

```sh
python3 sudoku.py run instances/slide.txt
```

Or one step at a time, looking at the files in between:

```sh
python3 sudoku.py encode instances/slide.txt sudoku.cnf   # puzzle -> formula
minisat sudoku.cnf sudoku.sol                             # formula -> satisfying interpretation
python3 sudoku.py decode sudoku.sol                       # interpretation -> grid
```

- `sudoku.cnf` is the formula in DIMACS CNF format, the input format of almost
  every SAT solver. The line `p cnf 729 3257` gives the number of variables and
  clauses. Every other line is one clause: a list of literals ending in `0`,
  where `n` stands for variable number n and `-n` for its negation. Variable
  v<sub>i,j,k</sub> is number 81(i&minus;1) + 9(j&minus;1) + k. Lines starting
  with `c` are comments marking where each part of &Phi; begins.
- `sudoku.sol` is MiniSat's answer: `UNSAT`, or `SAT` followed by the value of
  every variable (`n` for true, `-n` for false).

## Comparison: backtracking search

`backtracking.py` solves the same puzzles without logic: it fills in cells one
at a time and undoes its choices when it gets stuck.

```sh
python3 backtracking.py instances/slide.txt
```

## Instances

Nine rows of nine cells. Use digits for clues and `_` or `.` for empty cells;
spaces between cells are optional. Lines starting with `#` are comments.

| File | Contents |
|---|---|
| `instances/slide.txt` | the puzzle from the lecture slides |
| `instances/seventeen.txt` | a puzzle with only 17 clues |
| `instances/unsat.txt` | a puzzle with no solution |
| `instances/empty.txt` | an empty grid |

## Files

| File | Contents |
|---|---|
| `sudoku.py` | encoding, running MiniSat, decoding |
| `backtracking.py` | the backtracking solver |
| `board.py` | reading, printing and checking boards (used by both) |
