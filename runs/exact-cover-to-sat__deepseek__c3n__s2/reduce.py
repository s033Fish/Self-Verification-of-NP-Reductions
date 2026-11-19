"""Polynomial-time reduction from Exact Cover to SAT.

Source: {"universe_size": u, "sets": [[element, ...], ...]}
Target: {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea: introduce one boolean variable x_i for each set i, meaning
"set i is chosen".

  * For every element e of the universe, add the clause
        (x_i1 or x_i2 or ... or x_ik)
    where i1..ik are exactly the sets that contain e.  This forces e to be
    covered by at least one chosen set.  If no set contains e the clause is
    empty, which is unsatisfiable -- exactly right.

  * For every pair of distinct sets i < j whose intersection is non-empty,
    add the clause
        (-x_i or -x_j)
    so that two chosen sets can never share an element.  This also handles
    duplicate non-empty sets (they overlap, so they cannot both be chosen).

Empty sets produce variables that are unconstrained (they cover nothing and
overlap nothing), which is harmless.  For u = 0 there are no element clauses
and no overlapping pairs, so the formula is empty and satisfiable, matching
the convention that u = 0 is yes.

The construction uses O(u + n^2) clauses of length at most n, so it runs in
polynomial time and never calls a solver.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce an Exact Cover instance to a SAT instance (CNF)."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    num_sets = len(sets)

    # Precompute the element membership as python sets for fast intersection.
    set_elements = [set(s) for s in sets]

    clauses: list[list[int]] = []

    # 1. Coverage: every universe element must be in at least one chosen set.
    for element in range(universe_size):
        clause = [i + 1 for i in range(num_sets) if element in set_elements[i]]
        clauses.append(clause)

    # 2. Disjointness: overlapping sets cannot both be chosen.
    for i in range(num_sets):
        si = set_elements[i]
        for j in range(i + 1, num_sets):
            if not si.isdisjoint(set_elements[j]):
                clauses.append([-(i + 1), -(j + 1)])

    return {"num_vars": num_sets, "clauses": clauses}
