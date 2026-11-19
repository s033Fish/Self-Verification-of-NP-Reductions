"""Polynomial-time reduction from Exact Cover to SAT.

Exact Cover instance: {"universe_size": u, "sets": [[element, ...], ...]}
SAT instance:         {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce one SAT variable x_i for every set i (1-indexed, so variable i+1
for set index i).  x_i is true iff set i is chosen.

For every universe element e:
  * Let S_e be the indices of the sets that contain e.
  * Add the clause  [ i+1 for i in S_e ]  -- at least one chosen set must
    cover e.  If S_e is empty the clause is empty, which is unsatisfiable,
    correctly reflecting that e can never be covered.
  * For every pair i < j in S_e add the clause [-i-1, -j-1] -- at most one
    of the sets covering e may be chosen, i.e. chosen sets are disjoint.

A satisfying assignment selects exactly a pairwise-disjoint family of sets
whose union is the whole universe, i.e. an exact cover; conversely any exact
cover satisfies all clauses.  Empty sets never occur in any S_e, so their
variables are unconstrained (they can be freely set false).  Duplicate
non-empty sets share every element, so the pairwise clauses forbid choosing
both copies.

The number of clauses is O(u * n^2) and the construction runs in polynomial
time in the instance size.
"""


def reduce(instance):
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    num_vars = len(sets)
    clauses = []

    # For each element, the indices of the sets that contain it.
    covering = [[] for _ in range(universe_size)]
    for index, subset in enumerate(sets):
        for element in subset:
            covering[element].append(index)

    for indices in covering:
        if not indices:
            # No set can cover this element: unsatisfiable.
            clauses.append([])
            continue
        # At least one set covering this element is chosen.
        clauses.append([index + 1 for index in indices])
        # At most one such set is chosen (pairwise disjointness).
        for a in range(len(indices)):
            for b in range(a + 1, len(indices)):
                clauses.append([-(indices[a] + 1), -(indices[b] + 1)])

    return {"num_vars": num_vars, "clauses": clauses}
