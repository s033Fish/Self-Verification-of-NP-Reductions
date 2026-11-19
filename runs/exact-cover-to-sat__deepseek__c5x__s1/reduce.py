"""Polynomial-time reduction from Exact Cover to SAT.

Encoding
--------
Introduce one boolean variable x_i for each set i (variables 1..n).

Clauses:
  * For every universe element e, the clause
        [x_i for every set i containing e]
    forces e to be covered by at least one chosen set.
  * For every pair i < j of sets whose intersection is non-empty, the clause
        [-x_i, -x_j]
    forbids choosing both, i.e. chosen sets are pairwise disjoint.

A satisfying assignment selects a pairwise-disjoint family covering every
element, i.e. an exact cover (empty chosen sets can simply be discarded).
Conversely any exact cover extends to a satisfying assignment by setting the
chosen sets true and all others false.

Edge cases:
  * u = 0: no coverage clauses; all-false assignment satisfies everything, so
    the answer is yes, matching Exact Cover.
  * An element contained in no set yields the empty clause [], which is
    unsatisfiable, correctly reporting "no".
  * Duplicate non-empty sets intersect, so the disjointness clauses forbid
    choosing both copies.
  * Empty sets get an unconstrained variable; they never help or hurt.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Reduce an Exact Cover instance to a SAT instance."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    num_vars = len(sets)

    clauses: list[list[int]] = []

    # Coverage: each element must be in at least one chosen set.
    for element in range(universe_size):
        clause = [i + 1 for i, subset in enumerate(sets) if element in subset]
        clauses.append(clause)

    # Disjointness: no two sets sharing an element may both be chosen.
    for i in range(num_vars):
        set_i = set(sets[i])
        if not set_i:
            continue
        for j in range(i + 1, num_vars):
            if set_i & set(sets[j]):
                clauses.append([-(i + 1), -(j + 1)])

    return {"num_vars": num_vars, "clauses": clauses}
