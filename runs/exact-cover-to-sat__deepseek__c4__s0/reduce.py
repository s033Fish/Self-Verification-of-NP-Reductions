"""Polynomial-time reduction from Exact Cover to SAT.

Source instance: {"universe_size": u, "sets": [[element, ...], ...]}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce one boolean variable x_i for each set i (1-indexed).  x_i is true
means "set i is chosen".

Clauses:
  * Coverage: for every universe element e, add the clause
        [x_i for every set i that contains e]
    This forces at least one chosen set to cover e.  If no set contains e the
    clause is empty, which is unsatisfiable -- exactly right, since e cannot
    be covered.
  * Disjointness: for every pair i < j of sets whose intersection is
    non-empty, add the clause [-x_i, -x_j].  This forbids choosing both.

A satisfying assignment corresponds exactly to a sub-collection of sets that
is pairwise disjoint and covers the universe, i.e. an exact cover.  Empty
sets produce variables that appear in no clause (they are irrelevant, and an
empty set can never help cover anything).  Duplicate non-empty sets intersect
each other, so the disjointness clauses prevent choosing both copies.

The construction uses O(n^2) clauses where n is the number of sets, hence
runs in polynomial time.
"""

from __future__ import annotations


def reduce(instance):
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)

    # Precompute membership as sets for fast intersection tests.
    membership = [set(s) for s in sets]

    clauses = []

    # Coverage clauses: one per universe element.
    for element in range(universe_size):
        clause = [i + 1 for i in range(n) if element in membership[i]]
        clauses.append(clause)

    # Disjointness clauses: one per intersecting pair of sets.
    for i in range(n):
        si = membership[i]
        if not si:
            continue
        for j in range(i + 1, n):
            if si & membership[j]:
                clauses.append([-(i + 1), -(j + 1)])

    return {"num_vars": n, "clauses": clauses}
