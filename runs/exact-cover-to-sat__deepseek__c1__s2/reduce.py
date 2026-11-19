"""Polynomial-time reduction from Exact Cover to SAT.

Exact Cover instance:
    {"universe_size": u, "sets": [[element, ...], ...]}

SAT instance:
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce one Boolean variable x_i (1-based) for each set i, meaning
"set i is selected".

* Coverage: for every element e in 0..u-1, add the clause
      [x_i for every set i containing e]
  which forces at least one set containing e to be selected.  If no set
  contains e, this clause is empty, which is unsatisfiable -- exactly
  matching the fact that e cannot be covered.

* Disjointness: for every element e and every pair of distinct sets i < j
  that both contain e, add the clause [-x_i, -x_j].  This forbids choosing
  both i and j, i.e. it enforces that selected sets are pairwise disjoint.

A satisfying assignment selects a family of pairwise-disjoint sets whose
union is the whole universe, i.e. an exact cover, and conversely any exact
cover yields a satisfying assignment.  Empty sets create unconstrained
variables and never matter, and two copies of a non-empty set share an
element so the corresponding disjointness clause prevents choosing both.

The construction uses O(u + sum_i |set_i| + u * n^2) clauses where n is the
number of sets, which is polynomial in the input size.
"""


def reduce(instance):
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)

    # For each element, the indices of the sets that contain it.
    containing = [[] for _ in range(universe_size)]
    for index, subset in enumerate(sets):
        for element in set(subset):
            containing[element].append(index)

    clauses = []
    for element in range(universe_size):
        indices = containing[element]
        # At least one set covering this element must be selected.
        clauses.append([index + 1 for index in indices])
        # At most one of those sets may be selected (pairwise disjointness).
        for a in range(len(indices)):
            for b in range(a + 1, len(indices)):
                clauses.append([-(indices[a] + 1), -(indices[b] + 1)])

    return {"num_vars": n, "clauses": clauses}
