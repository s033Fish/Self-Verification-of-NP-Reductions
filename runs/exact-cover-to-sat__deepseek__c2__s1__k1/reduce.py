"""Polynomial-time reduction from Exact Cover to SAT.

Source instance: {"universe_size": u, "sets": [[element, ...], ...]}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Reduction
---------
One boolean variable x_i per input set (variable i+1 for set index i).
x_i is true iff set i is selected.

* For every universe element e, add the clause
      [x_i for every set i containing e]
  which says at least one selected set covers e.  If no set contains e this
  is the empty clause, which is unsatisfiable, exactly as it should be.

* For every pair of sets i < j whose intersection is non-empty, add the
  clause [-x_i, -x_j], saying the two sets are not both selected.  This
  enforces pairwise disjointness, i.e. no element is covered twice.

A satisfying assignment selects a pairwise-disjoint family of sets covering
every element: an exact cover.  Conversely an exact cover satisfies all
clauses.  The construction uses O(n^2) clauses and runs in polynomial time.
"""


def reduce(instance):
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)

    # Precompute membership as sets for fast intersection tests.
    members = [set(s) for s in sets]

    clauses = []

    # Cover every element at least once.
    for e in range(universe_size):
        clauses.append([i + 1 for i in range(n) if e in members[i]])

    # No two chosen sets may share an element.
    for i in range(n):
        mi = members[i]
        if not mi:
            continue
        for j in range(i + 1, n):
            if mi & members[j]:
                clauses.append([-(i + 1), -(j + 1)])

    return {"num_vars": n, "clauses": clauses}
