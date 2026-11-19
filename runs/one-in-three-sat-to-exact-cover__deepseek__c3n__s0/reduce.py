"""Polynomial-time reduction from 1-in-3-SAT (positive) to Exact Cover.

SOURCE: OneInThreeSat  instance {"num_vars": m, "clauses": [[a,b,c],...]}
TARGET: ExactCover     instance {"universe_size": u, "sets": [[e,...],...]}

Construction
------------
Elements:
  * x_i  (index i-1)         for each variable i in 1..m
  * y_j  (index m + j)       for each clause j (0-based)

Sets:
  * T_i = [x_i] + [y_j for every clause j containing variable i]
  * F_i = [x_i]

Every x_i occurs only in T_i and F_i, so an exact cover must pick exactly one
of them: picking T_i means "variable i is true" (and it covers every clause
element whose clause contains i); picking F_i means "variable i is false".

A clause element y_j occurs only in T_a, T_b, T_c where {a,b,c} are the
variables of clause j.  Since y_j must be covered exactly once, exactly one of
T_a, T_b, T_c is chosen, i.e. exactly one variable of the clause is true.

Conversely, a 1-in-3 satisfying assignment yields the exact cover
{ T_i : x_i true } u { F_i : x_i false }: each x_i is covered once and each
y_j is covered by exactly the one true variable of its clause, and the chosen
sets are pairwise disjoint (two chosen T's would share a y_j only if their
clauses both contained two true variables, impossible).

Edge cases: no clauses -> only the x_i elements and the T_i/F_i pairs, always
coverable; m = 0 -> u = 0, empty instance, yes.  Duplicate clauses give
distinct y_j elements, handled correctly.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 1-in-3-SAT instance to an Exact Cover instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    m = num_vars
    n = len(clauses)
    universe_size = m + n

    sets: list[list[int]] = []
    for i in range(1, m + 1):
        var_elem = i - 1
        true_set = [var_elem]
        for j, clause in enumerate(clauses):
            if i in clause:
                true_set.append(m + j)
        sets.append(true_set)   # T_i
        sets.append([var_elem])  # F_i

    return {"universe_size": universe_size, "sets": sets}
