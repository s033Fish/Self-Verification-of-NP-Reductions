"""Reduction from 3‑SAT to Exact Cover.

We use the standard polynomial‑time reduction:
  * Universe = {0,…,m‑1} for the variables plus {m,…,m+c‑1} for the clauses.
  * For each literal in clause j we create a set containing the variable
    element and the clause element.  Selecting this set corresponds to setting the
    variable so that the literal is true and using it to satisfy clause j.
  * For each variable i we also add a singleton set {i}.  This allows the exact
    cover to cover a variable that does not appear in any chosen literal set.

An exact cover must pick exactly one set containing each variable element and
exactly one set containing each clause element.  Therefore each clause is covered
by at least one of its literal sets, which yields a satisfying assignment.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a ThreeSat instance to an ExactCover instance.

    Input (ThreeSat): {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    Output (ExactCover): {"universe_size": u, "sets": [[e, ...], ...]}
    where u = m + c (c = number of clauses).
    """
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    c = len(clauses)

    universe_size = m + c
    sets: List[List[int]] = []

    # Literal sets: one for each literal occurrence.
    for j, clause in enumerate(clauses):
        clause_elem = m + j
        for lit in clause:
            var_idx = abs(lit) - 1  # variable element index
            sets.append([var_idx, clause_elem])

    # Singleton sets for each variable (allow it to be uncovered by literals).
    for i in range(m):
        sets.append([i])

    return {"universe_size": universe_size, "sets": sets}

