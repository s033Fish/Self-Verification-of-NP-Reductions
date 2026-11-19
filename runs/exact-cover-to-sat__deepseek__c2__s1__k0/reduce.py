"""Polynomial-time reduction from Exact Cover to SAT.

Exact Cover instance:
    {"universe_size": u, "sets": [[element, ...], ...]}

SAT instance:
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Reduction
---------
Introduce one boolean variable per set: variable i+1 corresponds to set i
being chosen.  Then:

* For every universe element e, add the clause of all positive literals
  (i+1) for sets i containing e.  This forces each element to be covered
  by at least one chosen set.
* For every pair of distinct sets i < j that share an element, add the
  clause [-(i+1), -(j+1)].  This forbids choosing both, so chosen sets
  are pairwise disjoint.

An assignment satisfying all clauses therefore selects a pairwise-disjoint
collection of sets whose union is the whole universe, i.e. an exact cover.
Conversely, any exact cover yields a satisfying assignment (set chosen
variables true; all others arbitrary).  Empty sets and elements contained
in no set are handled naturally: an uncovered element produces the empty
clause, which is unsatisfiable.

The formula has one variable per set, one clause per element, and at most
one clause per pair of sets, so it is built in polynomial time.
"""


def reduce(instance):
    """Reduce an Exact Cover instance to a SAT instance."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    num_sets = len(sets)

    clauses = []

    # Every element must be covered by at least one chosen set.
    for element in range(universe_size):
        clause = [i + 1 for i, subset in enumerate(sets) if element in subset]
        clauses.append(clause)

    # Chosen sets must be pairwise disjoint: forbid intersecting pairs.
    # Deduplicate pair clauses for efficiency; duplicate clauses are allowed
    # by SAT but need not be emitted.
    seen_pairs = set()
    for i in range(num_sets):
        set_i = sets[i]
        if not set_i:
            continue
        for j in range(i + 1, num_sets):
            set_j = sets[j]
            if not set_j:
                continue
            if seen_pairs and (i, j) in seen_pairs:
                continue
            if set(set_i).intersection(set_j):
                seen_pairs.add((i, j))
                clauses.append([-(i + 1), -(j + 1)])

    return {"num_vars": num_sets, "clauses": clauses}
