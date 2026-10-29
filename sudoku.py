"""Solve Sudoku by encoding it as propositional satisfiability (SAT).

The pipeline:

    puzzle file --encode--> CNF in DIMACS format --minisat--> model --decode--> solved grid

Each step can be run on its own:

    python3 sudoku.py encode instances/slide.txt sudoku.cnf
    minisat sudoku.cnf sudoku.sol
    python3 sudoku.py decode sudoku.sol

or all at once:

    python3 sudoku.py run instances/slide.txt
"""

import argparse
import subprocess
import sys

from board import BLOCK, N, NUMBERS, Board

# ---------------------------------------------------------------------------
# Variables
#
# v_{i,j,k} is true  <=>  cell (i, j) contains the number k.
# DIMACS names variables 1, 2, 3, ..., so we number them 81(i-1) + 9(j-1) + k.
# ---------------------------------------------------------------------------


def var(i, j, k):
    """The DIMACS number of the variable v_{i,j,k}."""
    return N * N * (i - 1) + N * (j - 1) + k


def unvar(n):
    """The inverse of var: the (i, j, k) that DIMACS variable n stands for."""
    n -= 1
    return n // (N * N) + 1, n // N % N + 1, n % N + 1


# ---------------------------------------------------------------------------
# The formula  Phi = phi_1 and phi_2 and phi_3 and phi_4 and phi_5 and phi_s
#
# Each function returns a list of clauses. A clause is a list of literals:
# n stands for v_{i,j,k} and -n for its negation, where n = var(i, j, k).
# ---------------------------------------------------------------------------


def phi_1():
    """At least one number per cell:  AND_{i,j}  OR_k  v_{i,j,k}"""
    clauses = []
    for i in NUMBERS:
        for j in NUMBERS:
            clause = []
            for k in NUMBERS:
                clause.append(var(i, j, k))
            clauses.append(clause)
    return clauses


def phi_2():
    """At most one number per cell:  AND_{i,j}  AND_{k<l}  not (v_{i,j,k} and v_{i,j,l})

    As a clause, not (a and b) is (not a or not b). Each pair k, l is needed
    only once: the clause for (l, k) would be the same clause again.
    """
    clauses = []
    for i in NUMBERS:
        for j in NUMBERS:
            for k in NUMBERS:
                for l in NUMBERS:
                    if k < l:
                        clause = [-var(i, j, k), -var(i, j, l)]
                        clauses.append(clause)
    return clauses


def phi_3():
    """Each number occurs in every row:  AND_{i,k}  OR_j  v_{i,j,k}"""
    clauses = []
    for i in NUMBERS:
        for k in NUMBERS:
            clause = []
            for j in NUMBERS:
                clause.append(var(i, j, k))
            clauses.append(clause)
    return clauses


def phi_4():
    """Each number occurs in every column:  AND_{j,k}  OR_i  v_{i,j,k}"""
    clauses = []
    for j in NUMBERS:
        for k in NUMBERS:
            clause = []
            for i in NUMBERS:
                clause.append(var(i, j, k))
            clauses.append(clause)
    return clauses


def phi_5():
    """Each number occurs in every block:  AND_{bi,bj,k}  OR_{di,dj}  v_{3bi+di, 3bj+dj, k}"""
    clauses = []
    for bi in range(BLOCK):
        for bj in range(BLOCK):
            for k in NUMBERS:
                clause = []
                for di in range(1, BLOCK + 1):
                    for dj in range(1, BLOCK + 1):
                        clause.append(var(BLOCK * bi + di, BLOCK * bj + dj, k))
                clauses.append(clause)
    return clauses


def phi_s(puzzle):
    """The clues of the puzzle:  AND_{puzzle places k on (i,j)}  v_{i,j,k}"""
    clauses = []
    for i, j, k in puzzle.clues():
        clauses.append([var(i, j, k)])
    return clauses


def encode(puzzle):
    """The formula Phi for the given puzzle, as a list of (name, clauses) parts."""
    return [
        ("phi_1: at least one number per cell", phi_1()),
        ("phi_2: at most one number per cell", phi_2()),
        ("phi_3: each number occurs in every row", phi_3()),
        ("phi_4: each number occurs in every column", phi_4()),
        ("phi_5: each number occurs in every block", phi_5()),
        ("phi_s: the clues", phi_s(puzzle)),
    ]


def count_clauses(parts):
    """The total number of clauses in all parts of the formula."""
    total = 0
    for name, clauses in parts:
        total += len(clauses)
    return total


def write_dimacs(parts, path):
    """Write the formula in DIMACS CNF format, with a comment line before each part."""
    num_clauses = count_clauses(parts)
    with open(path, "w", encoding="utf-8") as f:
        f.write("c Sudoku as SAT: v_{i,j,k} is variable 81(i-1) + 9(j-1) + k\n")
        f.write(f"p cnf {N ** 3} {num_clauses}\n")
        for name, clauses in parts:
            f.write(f"c {name} ({len(clauses)} clauses)\n")
            for clause in clauses:
                for literal in clause:
                    f.write(f"{literal} ")
                f.write("0\n")


# ---------------------------------------------------------------------------
# Solving and decoding
# ---------------------------------------------------------------------------


def run_minisat(cnf_path, sol_path):
    """Run MiniSat on cnf_path; it writes its result to sol_path."""
    try:
        result = subprocess.run(["minisat", cnf_path, sol_path])
    except FileNotFoundError:
        sys.exit("minisat not found; see the README for how to install it")
    # MiniSat's exit code is 10 for satisfiable and 20 for unsatisfiable.
    if result.returncode not in (10, 20):
        sys.exit(f"minisat failed with exit code {result.returncode}")


def decode(sol_path):
    """Read MiniSat's result file. Return the solved Board, or None if unsatisfiable.

    The file is either the line UNSAT, or the line SAT followed by the model:
    a list of literals ending in 0. Literal n means variable n is true,
    -n means it is false.
    """
    with open(sol_path, encoding="utf-8") as f:
        status = f.readline().strip()
        if status == "UNSAT":
            return None
        if status != "SAT":
            raise ValueError(f"{sol_path}: expected SAT or UNSAT, found {status!r}")
        model = f.read().split()

    # phi_1 and phi_2 guarantee exactly one true v_{i,j,k} for every cell.
    solution = Board()
    for word in model:
        literal = int(word)
        if literal > 0:
            i, j, k = unvar(literal)
            solution[i, j] = k
    return solution


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------


def cmd_encode(puzzle_path, cnf_path):
    puzzle = Board.from_file(puzzle_path)
    parts = encode(puzzle)
    write_dimacs(parts, cnf_path)
    print(f"Wrote {cnf_path}: {N ** 3} variables, "
          f"{count_clauses(parts)} clauses")
    for name, clauses in parts:
        print(f"  {name}: {len(clauses)}")
    return puzzle


def cmd_decode(sol_path):
    solution = decode(sol_path)
    if solution is None:
        print("Unsatisfiable: this puzzle has no solution.")
    else:
        print(solution)
    return solution


def cmd_run(puzzle_path, cnf_path, sol_path):
    puzzle = cmd_encode(puzzle_path, cnf_path)
    print()
    print(puzzle)
    print()
    run_minisat(cnf_path, sol_path)
    print()
    solution = cmd_decode(sol_path)
    if solution is not None:
        print()
        print("Correct solution." if solution.is_solution_of(puzzle)
              else "Not a correct solution: the encoding has a bug!")


def main():
    parser = argparse.ArgumentParser(description="Solve Sudoku with a SAT solver.")
    commands = parser.add_subparsers(dest="command", required=True)

    p = commands.add_parser("encode", help="write the puzzle as a CNF formula in DIMACS format")
    p.add_argument("puzzle")
    p.add_argument("cnf", nargs="?", default="sudoku.cnf")

    p = commands.add_parser("decode", help="turn MiniSat's result file back into a grid")
    p.add_argument("solution", nargs="?", default="sudoku.sol")

    p = commands.add_parser("run", help="encode, run MiniSat and decode")
    p.add_argument("puzzle")
    p.add_argument("--cnf", default="sudoku.cnf")
    p.add_argument("--solution", default="sudoku.sol")

    args = parser.parse_args()
    try:
        if args.command == "encode":
            cmd_encode(args.puzzle, args.cnf)
        elif args.command == "decode":
            cmd_decode(args.solution)
        else:
            cmd_run(args.puzzle, args.cnf, args.solution)
    except (OSError, ValueError) as error:
        sys.exit(f"error: {error}")


if __name__ == "__main__":
    main()
