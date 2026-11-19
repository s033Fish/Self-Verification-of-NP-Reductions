"""Polynomial-time reduction from Exact Cover to SAT.

Idea
----
Introduce one boolean variable x_i per input set i (1-indexed), meaning
"set i is chosen".

  * For every universe element e, emit the clause
        [x_i for every set i containing e]
    forcing at least one chosen set to contain e (coverage).

  * For every pair of distinct sets i < j whose intersection is non-empty,
    emit the clause [-x_i, -x_j]
    forcing that the two are not both chosen (disjointness).

If every element is covered at least once and the chosen sets are pairwise
disjoint, then every element is covered exactly once, so the chosen sets form
an exact cover.  Conversely any exact cover satisfies all clauses (pick the
indicator assignment of the chosen sets).

Empty sets: their variable never occurs in a coverage clause and they
intersect nothing, so they are unconstrained -- they never matter, matching
the source semantics.  Two copies of the same non-empty set intersect, so the
disjointness clause forbids choosing both.  For u = 0 there are no coverage
clauses and all sets are empty, so the formula has no clauses and is
satisfiable, matching "u = 0 is yes".

The construction uses O(u * n + n^2) clauses and runs in polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)

    # Precompute membership as sets for the pairwise-intersection step.
    as_sets = [set(s) for s in sets]

    clauses: list[list[int]] = []

    # Coverage: element e must be contained in at least one chosen set.
    # An element contained in no set yields the empty clause -> unsatisfiable.
    for e in range(universe_size):
        clause = [i + 1 for i in range(n) if e in as_sets[i]]
        clauses.append(clause)

    # Disjointness: intersecting sets cannot both be chosen.
    for i in range(n):
        si = as_sets[i]
        if not si:
            continue  # empty set intersects nothing
        for j in range(i + 1, n):
            if si & as_sets[j]:
                clauses.append([-(i + 1), -(j + 1)])

    return {"num_vars": n, "clauses": clauses}
