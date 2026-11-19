"""Polynomial-time reduction from Exact Cover to SAT.

Source (ExactCover): {"universe_size": u, "sets": [[element, ...], ...]}
Target (Sat):         {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce one boolean variable x_i for every set i (variables 1..len(sets)).

* Covering: for every universe element e, add the clause
      [x_i for every set i containing e]
  This forces at least one chosen set to contain e.

* Disjointness: for every pair of distinct sets i < j that share at least
  one element, add the clause [-x_i, -x_j].
  This forbids choosing two sets that overlap.

A satisfying assignment selects exactly the sets whose variable is true.
Every element is covered (covering clauses) and no two selected sets overlap
(disjointness clauses), so the selected sets form an exact cover.  Conversely
any exact cover yields a satisfying assignment by setting its sets true.

Edge cases
----------
* u = 0: no covering clauses; if sets are non-empty the instance is invalid
  anyway (elements must be < 0), so all sets are empty and there are no
  overlap clauses either.  The formula has no clauses and is satisfiable,
  matching "u = 0 is yes".
* Empty sets: their variable never occurs in a clause, so it is free and
  never affects satisfiability, matching "empty sets never matter".
* Duplicate non-empty sets: they overlap, so the disjointness clause forbids
  choosing both, matching "two copies of the same non-empty set can never
  both be chosen".
* An element contained in no set produces the empty clause [], which is
  unsatisfiable, correctly making the instance a "no".
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Return a SAT instance that is satisfiable iff the Exact Cover
    instance has an exact cover."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)

    clauses: list[list[int]] = []

    # Covering clauses: at least one set containing each element must be chosen.
    # For each element collect the indices of sets that contain it.
    containing: list[list[int]] = [[] for _ in range(universe_size)]
    for index, subset in enumerate(sets):
        for element in subset:
            containing[element].append(index)

    for element in range(universe_size):
        # Clause of positive literals (index + 1).  May be empty, which
        # correctly makes the formula unsatisfiable when no set covers it.
        clauses.append([index + 1 for index in containing[element]])

    # Disjointness clauses: forbid choosing two sets that share an element.
    # For each element, every pair of sets containing it must not both be
    # chosen.  Emitting these per element avoids an O(n^2) pairwise scan.
    for element in range(universe_size):
        indices = containing[element]
        for a in range(len(indices)):
            for b in range(a + 1, len(indices)):
                i = indices[a]
                j = indices[b]
                clauses.append([-(i + 1), -(j + 1)])

    return {"num_vars": n, "clauses": clauses}
