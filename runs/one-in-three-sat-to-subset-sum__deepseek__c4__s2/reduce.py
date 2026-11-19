"""Polynomial-time reduction from 1-in-3-SAT (OneInThreeSat) to Subset Sum.

Construction
------------
Let m = num_vars and n = number of clauses.  Work in base B (a digit
position for every variable and every clause).  Variable i gets digit
position i-1, clause j gets digit position m+j.

For every variable i we create two numbers:

    y_i = B^(i-1) + sum over clauses j containing i of B^(m+j)
    z_i = B^(i-1)

Selecting y_i means "x_i is true", selecting z_i means "x_i is false".

The target has digit 1 in every variable position and digit 1 in every
clause position:

    target = sum_i B^(i-1) + sum_j B^(m+j)

Why it works
------------
* A variable digit position receives contributions only from y_i and z_i
  (each contributes exactly 1), so any subset summing to the target must
  contain exactly one of them.  Hence every variable gets a definite truth
  value.
* A clause digit position receives a contribution of 1 from y_i exactly
  when variable i occurs in that clause.  With the truth values fixed above,
  the digit equals the number of true variables in the clause.  The target
  requires it to be exactly 1, i.e. exactly one true variable per clause.

Every digit position sums to at most 3 (a clause has 3 distinct variables),
so with B = 10 there are no carries and the digit-wise argument is exact.

Edge cases: no clauses -> target has only variable digits, and y_i = z_i for
all i, so picking one per variable works (yes).  m = n = 0 -> empty list,
target 0 (yes).
"""

from __future__ import annotations

BASE = 10


def reduce(instance: dict) -> dict:
    """Reduce a 1-in-3-SAT instance to a Subset Sum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    n = len(clauses)

    # clause_occurs[i] = list of clause indices containing variable i (1-indexed)
    clause_occurs = [[] for _ in range(num_vars + 1)]
    for j, clause in enumerate(clauses):
        for var in clause:
            clause_occurs[var].append(j)

    numbers = []
    for i in range(1, num_vars + 1):
        var_digit = BASE ** (i - 1)
        y = var_digit
        for j in clause_occurs[i]:
            y += BASE ** (num_vars + j)
        z = var_digit
        numbers.append(y)
        numbers.append(z)

    target = 0
    for i in range(1, num_vars + 1):
        target += BASE ** (i - 1)
    for j in range(n):
        target += BASE ** (num_vars + j)

    return {"numbers": numbers, "target": target}
