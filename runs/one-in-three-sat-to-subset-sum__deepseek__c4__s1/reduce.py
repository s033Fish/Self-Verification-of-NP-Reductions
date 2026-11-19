"""Polynomial-time reduction from 1-in-3-SAT to Subset Sum.

Encoding
--------
Fix a base B (we use B = 10).  A number is represented by its base-B digits.
We reserve one digit position per variable (positions 0 .. m-1) and one digit
position per clause (positions m .. m+n-1).

For every variable i (1..m) we create two numbers:

    T_i = B^(i-1) + sum over clauses j containing i of B^(m+j-1)
    F_i = B^(i-1)

The variable digit forces exactly one of T_i / F_i to be selected (target has
a 1 there, all numbers are non-negative, and no carries happen because the
digit sums stay below B).  Selecting T_i means "variable i is true"; it adds 1
to the digit of every clause containing i.  Selecting F_i means "variable i is
false" and adds nothing to clause digits.

The target has a 1 in every variable digit and a 1 in every clause digit.
Thus a solution picks exactly one of T_i/F_i per variable, and for every clause
the number of selected true variables in it equals exactly 1.

Since at most 3 numbers contribute to any clause digit and at most 2 to any
variable digit, base B = 10 guarantees there are no carries.

Edge cases:
  * no clauses -> target = sum of variable digits, always achievable by
    picking one number per variable; instance is yes.
  * m = 0, no clauses -> numbers = [], target = 0 -> yes (empty sub-list).
"""

from __future__ import annotations

from typing import Any

BASE = 10


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    # clause_of_var[i] = list of clause indices containing variable i (0-based)
    clause_of_var: list[list[int]] = [[] for _ in range(num_vars)]
    for j, clause in enumerate(clauses):
        for var in clause:
            clause_of_var[var - 1].append(j)

    numbers: list[int] = []
    target = 0

    # variable digit positions 0 .. num_vars-1
    for i in range(num_vars):
        var_digit = BASE ** i
        true_number = var_digit
        for j in clause_of_var[i]:
            true_number += BASE ** (num_vars + j)
        numbers.append(true_number)   # variable i true
        numbers.append(var_digit)     # variable i false
        target += var_digit

    # clause digit positions num_vars .. num_vars+num_clauses-1
    for j in range(num_clauses):
        target += BASE ** (num_vars + j)

    return {"numbers": numbers, "target": target}
