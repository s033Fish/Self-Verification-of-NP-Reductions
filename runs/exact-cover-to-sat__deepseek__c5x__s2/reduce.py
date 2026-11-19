"""Polynomial-time reduction from Exact Cover to SAT.

Exact Cover instance: {"universe_size": u, "sets": [[element, ...], ...]}
SAT instance:         {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction: introduce one boolean variable x_i for each input set i
(1-indexed).  x_i is true iff set i is chosen.

  * For every universe element e, add the clause of all positive literals
    x_i for sets i containing e.  This forces at least one chosen set to
    cover e.
  * For every pair of distinct sets i, j that share at least one element,
    add the clause (-x_i, -x_j).  This forbids choosing both, i.e. it
    enforces pairwise disjointness of the chosen sets.

The chosen sets then cover every element at least once and are pairwise
disjoint, so they cover every element exactly once.  Conversely any exact
cover satisfies all clauses.  The construction is polynomial: at most u
coverage clauses plus O(sum_e k_e^2) disjointness clauses, where k_e is the
number of sets containing element e.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    num_sets = len(sets)

    # sets_containing[e] = list of 1-indexed variables of sets containing e
    sets_containing: list[list[int]] = [[] for _ in range(universe_size)]
    for index, subset in enumerate(sets):
        var = index + 1
        for element in subset:
            sets_containing[element].append(var)

    clauses: list[list[int]] = []

    for element in range(universe_size):
        vars_here = sets_containing[element]
        # At least one set covering this element must be chosen.
        clauses.append(list(vars_here))
        # At most one set covering this element may be chosen.
        for a in range(len(vars_here)):
            for b in range(a + 1, len(vars_here)):
                clauses.append([-vars_here[a], -vars_here[b]])

    return {"num_vars": num_sets, "clauses": clauses}
