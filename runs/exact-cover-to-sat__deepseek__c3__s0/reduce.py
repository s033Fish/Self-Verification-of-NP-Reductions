"""Polynomial-time reduction from Exact Cover to SAT.

Exact Cover instance: {"universe_size": u, "sets": [[element, ...], ...]}
SAT instance:         {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce one boolean variable x_i for each set i (so m = len(sets)):
x_i is true iff set i is chosen.

* For every universe element e, add the clause
      [x_i for every set i that contains e]
  This forces at least one chosen set to cover e.  If no set contains e the
  clause is empty, which is unsatisfiable -- correct, since e cannot be
  covered.

* For every pair of distinct sets i < j that share at least one element,
  add the clause [-x_i, -x_j].  This forbids choosing both, i.e. it enforces
  pairwise disjointness of the chosen sets.

A satisfying assignment therefore selects a pairwise-disjoint family of sets
covering every element exactly once, and conversely any exact cover yields a
satisfying assignment.  Empty sets produce variables that appear in no
element clause; they may be freely chosen or not, matching the fact that
empty sets never matter.  Duplicate non-empty sets overlap, so the overlap
clause prevents choosing both copies.  For u = 0 there are no element
clauses and the all-false assignment satisfies the formula (yes).

The construction uses O(len(sets)^2) clauses and runs in polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce an Exact Cover instance to a SAT instance."""
    universe_size: int = instance["universe_size"]
    sets: list[list[int]] = instance["sets"]

    num_sets = len(sets)

    # Element coverage clauses: for each element, the sets containing it.
    clauses: list[list[int]] = []
    for element in range(universe_size):
        clause = [
            i + 1
            for i, subset in enumerate(sets)
            if element in subset
        ]
        clauses.append(clause)

    # Pairwise-disjointness clauses for overlapping sets.
    # Represent each set as a frozenset of its elements for quick intersection.
    element_sets = [frozenset(subset) for subset in sets]
    for i in range(num_sets):
        si = element_sets[i]
        if not si:
            continue
        for j in range(i + 1, num_sets):
            if si & element_sets[j]:
                clauses.append([-(i + 1), -(j + 1)])

    return {"num_vars": num_sets, "clauses": clauses}
