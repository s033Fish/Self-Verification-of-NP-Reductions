"""Polynomial-time reduction from 1-in-3-SAT to Exact Cover.

Construction
------------
Given a positive 1-in-3-SAT instance with m variables (1..m) and clauses
clauses[0..C-1]:

* Universe element e_i (index i-1) represents variable i.
* Universe element d_j (index m+j) represents clause j.

* For each variable i:
    - "true" set  T_i = {e_i} U {d_j : variable i occurs in clause j}
    - "false" set F_i = {e_i}

An exact cover must cover e_i exactly once, so for each variable exactly one
of T_i / F_i is chosen.  Element d_j is contained only in the sets T_i for
variables i occurring in clause j.  Since chosen sets must be pairwise
disjoint and must cover d_j, exactly one variable of clause j must have its
T set chosen, i.e. exactly one variable of the clause is true.  Hence exact
covers correspond bijectively to satisfying assignments.

The instance has m + C universe elements and 2m sets whose total size is
O(m + number of variable occurrences), so the reduction is polynomial.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    num_clauses = len(clauses)
    universe_size = num_vars + num_clauses

    # For each variable, collect the clause indices in which it occurs.
    occurrence: dict[int, list[int]] = {v: [] for v in range(1, num_vars + 1)}
    for j, clause in enumerate(clauses):
        for var in clause:
            occurrence[var].append(j)

    sets: list[list[int]] = []
    for v in range(1, num_vars + 1):
        e = v - 1  # element representing variable v
        true_set = [e] + [num_vars + j for j in occurrence[v]]
        false_set = [e]
        sets.append(true_set)
        sets.append(false_set)

    return {"universe_size": universe_size, "sets": sets}
