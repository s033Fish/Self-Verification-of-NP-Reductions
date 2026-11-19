"""Polynomial-time reduction from 1-in-3-SAT to Subset Sum.

Construction (no slack gadgets needed because 1-in-3-SAT demands EXACTLY one
true variable per clause):

Choose a base B = 10.  There is one digit column per variable (columns
0..m-1) and one digit column per clause (columns m..m+n-1).

For every variable i in 1..m create two numbers:
  * T_i (i is true):  digit 1 in variable-column i-1, and digit 1 in
    clause-column m+j for every clause j that contains i.
  * F_i (i is false): digit 1 in variable-column i-1 only.

The target has digit 1 in every column.

A variable column can only receive contributions from T_i and F_i, so the
target digit 1 forces exactly one of them to be selected.  A clause column
receives a contribution from T_i exactly when variable i is set true, so its
sum equals the number of true variables in that clause; the target digit 1
forces that number to be exactly one.  Every digit is at most 3 < B, so no
carries occur and integer equality is digit-wise equality.
"""

from __future__ import annotations

from typing import Any

BASE = 10


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 1-in-3-SAT instance to a Subset Sum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    m = num_vars
    n = len(clauses)

    numbers: list[int] = []
    for i in range(1, m + 1):
        var_digit = BASE ** (i - 1)
        true_number = var_digit
        for j, clause in enumerate(clauses):
            if i in clause:
                true_number += BASE ** (m + j)
        numbers.append(true_number)  # T_i
        numbers.append(var_digit)    # F_i

    target = 0
    for i in range(1, m + 1):
        target += BASE ** (i - 1)
    for j in range(n):
        target += BASE ** (m + j)

    return {"numbers": numbers, "target": target}
