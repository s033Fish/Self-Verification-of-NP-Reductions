"""Polynomial-time reduction from 3-SAT (ThreeSat) to Subset Sum (SubsetSum).

Standard digit-encoding reduction (Sipser-style).

Let m = num_vars and k = number of clauses.  Work in base 10 and use
m + k digit positions:

    * positions 0 .. m-1        correspond to variables 1 .. m
    * positions m .. m+k-1      correspond to clauses 0 .. k-1

For every variable i we create two numbers:
    T_i : digit (i-1) = 1, and digit (m+j) = 1 for every clause j
          containing the literal +i.
    F_i : digit (i-1) = 1, and digit (m+j) = 1 for every clause j
          containing the literal -i.

For every clause j we create two identical "slack" numbers:
    S_j, S'_j : digit (m+j) = 1.

The target has digit 1 in every variable position and digit 3 in every
clause position.

Why it works: no column ever receives more than 5 (three literal
contributions plus two slack contributions), so base 10 has no carries and
the digits can be read independently.  In variable position i exactly one
of T_i, F_i must be selected (0 or 2 cannot equal 1), which encodes a
truth assignment.  In clause position j the selected slacks contribute
0, 1 or 2, so the selected literals must contribute 3, 2 or 1 respectively
-- in every case at least one literal of the clause is true.  Conversely a
satisfying assignment selects exactly one number per variable and the
slacks needed to fill each clause column to 3.

The construction is linear in the size of the formula, hence polynomial.
"""

from __future__ import annotations

from typing import Any

BASE = 10


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to a Subset Sum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    m = num_vars
    k = len(clauses)
    total = m + k

    def make(digits: dict[int, int]) -> int:
        """Build an integer whose base-BASE digits are given by `digits`."""
        value = 0
        for pos, count in digits.items():
            value += count * (BASE ** (total - 1 - pos))
        return value

    numbers: list[int] = []

    # One number per variable for the true literal and one for the false.
    for i in range(1, m + 1):
        true_digits = {i - 1: 1}
        false_digits = {i - 1: 1}
        for j, clause in enumerate(clauses):
            pos = m + j
            if i in clause:
                true_digits[pos] = true_digits.get(pos, 0) + 1
            if -i in clause:
                false_digits[pos] = false_digits.get(pos, 0) + 1
        numbers.append(make(true_digits))
        numbers.append(make(false_digits))

    # Two slack numbers per clause.
    for j in range(k):
        pos = m + j
        numbers.append(make({pos: 1}))
        numbers.append(make({pos: 1}))

    target_digits: dict[int, int] = {}
    for i in range(1, m + 1):
        target_digits[i - 1] = 1
    for j in range(k):
        target_digits[m + j] = 3

    return {"numbers": numbers, "target": make(target_digits)}
