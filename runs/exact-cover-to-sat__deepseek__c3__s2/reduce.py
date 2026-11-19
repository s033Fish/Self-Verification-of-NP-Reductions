"""Polynomial-time reduction from Exact Cover to SAT.

Exact Cover instance: {"universe_size": u, "sets": [[element, ...], ...]}
SAT instance:         {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce one boolean variable x_i for each set i (variable number i+1),
meaning "set i is chosen".

Clauses:
  * For every element e of the universe, one clause containing the positive
    literals x_i for all sets i that contain e.  This forces at least one
    chosen set to cover e.
  * For every pair of distinct set indices i < j that share at least one
    element, the clause (-x_i or -x_j).  This forbids choosing two sets that
    overlap.

A satisfying assignment therefore selects a family of pairwise disjoint sets
whose union is the whole universe, i.e. an exact cover, and every exact cover
yields a satisfying assignment.  Empty sets contribute no literals anywhere,
so they are irrelevant; two copies of the same non-empty set share elements
and thus get a mutual-exclusion clause.

The number of clauses is at most u + (number of overlapping pairs), which is
polynomial in the input size.
"""


def reduce(instance):
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)

    # For each element, the list of set indices containing it.
    containing = [[] for _ in range(universe_size)]
    for i, subset in enumerate(sets):
        for element in subset:
            containing[element].append(i)

    clauses = []

    # Coverage clauses: every element must be covered by some chosen set.
    for element in range(universe_size):
        clauses.append([i + 1 for i in containing[element]])

    # Disjointness clauses: sets sharing an element cannot both be chosen.
    # Iterate over elements and add a clause for each pair of sets sharing it.
    seen_pairs = set()
    for element in range(universe_size):
        idxs = containing[element]
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                i, j = idxs[a], idxs[b]
                pair = (i, j)
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                clauses.append([-(i + 1), -(j + 1)])

    return {"num_vars": n, "clauses": clauses}
