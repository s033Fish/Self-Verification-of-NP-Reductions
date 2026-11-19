"""Polynomial-time reduction from Exact Cover to SAT.

SOURCE = ExactCover
    {"universe_size": u, "sets": [[element, ...], ...]}
TARGET = Sat
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Reduction
---------
Introduce one boolean variable per set: variable ``i + 1`` is true iff set
``i`` is chosen.  Then build clauses:

* Coverage: for every element ``e`` in ``0..u-1`` add the clause containing
  ``i + 1`` for every set ``i`` that contains ``e``.  Satisfying it means at
  least one chosen set contains ``e``.
* Disjointness: for every pair of sets ``i < j`` whose intersection is
  non-empty add the clause ``[-(i + 1), -(j + 1)]``, forbidding choosing both.

A satisfying assignment therefore selects a sub-collection of sets that covers
every element (coverage clauses) and is pairwise disjoint (disjointness
clauses), i.e. an exact cover.  Conversely any exact cover gives a satisfying
assignment by setting exactly the chosen sets' variables true.

Edge cases:
* ``u == 0``: no coverage clauses; if no two sets overlap there are no clauses
  at all, which is satisfiable -> yes (choose no sets), matching Exact Cover.
* Empty sets: contain no element, so they never occur in a coverage clause and
  never overlap another set, so their variables are unconstrained (free).
* Duplicate non-empty sets: they overlap, so the disjointness clause forbids
  choosing both, matching "two copies can never both be chosen".
* ``u > 0`` and no set covers some element: the coverage clause is empty ``[]``,
  which is unsatisfiable -> no.

The construction is polynomial: O(u * n) for coverage plus O(n^2 * u) for the
pairwise checks, where n is the number of sets.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Reduce an Exact Cover instance to a SAT instance."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)

    # Precompute, for each element, the list of set indices containing it.
    containing: list[list[int]] = [[] for _ in range(universe_size)]
    for i, subset in enumerate(sets):
        for element in subset:
            containing[element].append(i)

    clauses: list[list[int]] = []

    # Coverage clauses: element e must be covered by at least one chosen set.
    for element in range(universe_size):
        clauses.append([i + 1 for i in containing[element]])

    # Disjointness clauses: overlapping sets cannot both be chosen.
    for i in range(n):
        set_i = set(sets[i])
        if not set_i:
            continue
        for j in range(i + 1, n):
            if set_i.intersection(sets[j]):
                clauses.append([-(i + 1), -(j + 1)])

    return {"num_vars": n, "clauses": clauses}
