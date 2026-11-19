"""Polynomial-time reduction from 1-in-3-SAT to Subset Sum.

Encoding idea
-------------
Work in base B = 4.  Each number is written with (m + n) digits, where
m = num_vars and n = number of clauses:

    digit positions 0 .. m-1      -> one "variable" position per variable
    digit positions m .. m+n-1    -> one "clause" position per clause

For every variable i (1-based) we create two numbers:

    T_i = B^(i-1) + sum_{clause j containing i} B^(m+j)   (variable i true)
    F_i = B^(i-1)                                          (variable i false)

The target is

    target = sum_{i=1..m} B^(i-1) + sum_{j=0..n-1} B^(m+j)

Correctness
-----------
Every digit position receives a sum of at most 3 (a variable position gets at
most the two numbers T_i, F_i; a clause position gets at most the three
variables of that clause), and 3 < B = 4, so there are never any carries.
Hence a subset sums to target iff it matches the target digit by digit:

  * variable position i must sum to 1  -> exactly one of T_i, F_i is chosen,
    i.e. variable i gets a well defined truth value;
  * clause position j must sum to 1    -> exactly one variable of clause j is
    chosen as true.

So a subset summing to target exists iff the formula is 1-in-3 satisfiable.
The construction is clearly polynomial in the instance size.
"""

from __future__ import annotations

from typing import Any

BASE = 4


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 1-in-3-SAT instance to a Subset Sum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    # clause_in_vars[i] = list of clause indices containing variable i (0-based i)
    clause_in_vars: list[list[int]] = [[] for _ in range(num_vars)]
    for j, clause in enumerate(clauses):
        for var in clause:
            clause_in_vars[var - 1].append(j)

    numbers: list[int] = []
    target = 0

    for i in range(num_vars):
        var_digit = BASE ** i
        target += var_digit
        true_number = var_digit
        for j in clause_in_vars[i]:
            true_number += BASE ** (num_vars + j)
        numbers.append(true_number)  # T_i
        numbers.append(var_digit)    # F_i

    for j in range(num_clauses):
        target += BASE ** (num_vars + j)

    return {"numbers": numbers, "target": target}
