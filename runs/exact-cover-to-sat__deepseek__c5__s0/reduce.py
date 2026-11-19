"""Polynomial-time reduction from Exact Cover to SAT.

Exact Cover instance: {"universe_size": u, "sets": [[element, ...], ...]}
SAT instance:         {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce one boolean variable x_i for every set S_i (variable i+1).  The
intended meaning of x_i is "set S_i is chosen".

* For every universe element e, add the clause
      ( x_i1 OR x_i2 OR ... )
  over all sets containing e.  This forces e to be covered by at least one
  chosen set.  If no set contains e, this clause is empty and the formula is
  unsatisfiable, matching the fact that e can never be covered.

* For every universe element e and every pair i < j of distinct sets that
  both contain e, add the clause
      ( -x_i OR -x_j )
  forbidding both sets from being chosen.  Together with the covering
  clauses this makes the chosen sets pairwise disjoint on every element.

Empty sets produce no covering or disjointness clauses, so their variables are
unconstrained, exactly as empty sets never matter in Exact Cover.  Duplicate
sets are handled because two copies sharing a non-empty element get a
disjointness clause and can never both be selected.  For u = 0 no clauses are
produced and the empty formula is satisfiable, matching "u = 0 is yes".

The number of clauses is at most u + u * |sets|^2, which is polynomial in the
input size.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce an Exact Cover instance to a SAT instance."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    num_vars = len(sets)
    clauses = []

    # For each element, collect the indices of sets containing it.
    covering = [[] for _ in range(universe_size)]
    for index, subset in enumerate(sets):
        for element in subset:
            covering[element].append(index)

    for element in range(universe_size):
        indices = covering[element]
        # At least one chosen set must cover this element.
        clauses.append([index + 1 for index in indices])
        # At most one chosen set may cover this element.
        for a in range(len(indices)):
            for b in range(a + 1, len(indices)):
                clauses.append([-(indices[a] + 1), -(indices[b] + 1)])

    return {"num_vars": num_vars, "clauses": clauses}
