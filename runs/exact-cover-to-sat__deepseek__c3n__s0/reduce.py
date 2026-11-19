"""Polynomial-time reduction from Exact Cover to SAT.

Source instance: {"universe_size": u, "sets": [[element, ...], ...]}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
-----------
Introduce one boolean variable x_i for every set i (variables are 1..m with
m = len(sets)).  The intended meaning is "set i is chosen".

1. For every universe element e, add the clause
       [i+1 for each set i containing e]
   which says at least one chosen set covers e.

2. For every pair of distinct sets i < j that share at least one element,
   add the clause [-(i+1), -(j+1)] i.e. [-i-1, -j-1], which says the two
   sets cannot both be chosen (they would overlap).

A satisfying assignment selects a family of pairwise disjoint sets that
covers every element, i.e. an exact cover; conversely an exact cover gives
a satisfying assignment by setting x_i true for chosen sets.

Edge cases
----------
* u = 0: no element clauses and no overlap clauses -> empty CNF, satisfiable.
* An element covered by no set yields the empty clause [] -> unsatisfiable.
* Empty sets produce a variable that appears in no clause; harmless.
* Duplicate non-empty sets share elements, so the pairwise clauses forbid
  choosing both copies.

The construction uses O(u + sum_e k_e^2) clauses where k_e is the number of
sets containing element e, hence polynomial time and size.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce an Exact Cover instance to a SAT instance."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    num_vars = len(sets)
    clauses: list[list[int]] = []

    # sets_containing[e] = list of set indices that contain element e
    sets_containing: list[list[int]] = [[] for _ in range(universe_size)]
    for index, subset in enumerate(sets):
        for element in subset:
            sets_containing[element].append(index)

    # 1. Coverage clauses: every element must be covered by some chosen set.
    for element in range(universe_size):
        clauses.append([index + 1 for index in sets_containing[element]])

    # 2. Disjointness clauses: any two sets sharing an element cannot both be
    #    chosen.  For each element, all pairs among the sets containing it.
    for element in range(universe_size):
        indices = sets_containing[element]
        for a in range(len(indices)):
            for b in range(a + 1, len(indices)):
                i = indices[a]
                j = indices[b]
                clauses.append([-(i + 1), -(j + 1)])

    return {"num_vars": num_vars, "clauses": clauses}
