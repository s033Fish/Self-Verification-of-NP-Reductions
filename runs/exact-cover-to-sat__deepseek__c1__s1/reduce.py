"""Polynomial-time reduction from Exact Cover to SAT.

Source instance (Exact Cover):
    {"universe_size": u, "sets": [[element, ...], ...]}

Target instance (SAT):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce one boolean variable x_i for every set i (1-indexed).  Intuitively
x_i is true iff set i is chosen for the cover.

1. Cover every element: for each element e in 0..u-1 add the clause

       (x_i1 OR x_i2 OR ... OR x_ik)

   over all sets i that contain e.  This forces each element to be covered by
   at least one chosen set.  If no set contains e the clause is empty, which is
   unsatisfiable, correctly reflecting that e cannot be covered.

2. Enforce disjointness: for every pair of distinct sets i < j whose
   intersection is non-empty add the clause

       (~x_i OR ~x_j)

   so two chosen sets may never share an element.  In particular two copies of
   the same non-empty set can never both be chosen.

The chosen sets are therefore pairwise disjoint and cover the whole universe,
i.e. exactly an exact cover.  Empty sets have empty masks: they never take part
in a disjointness clause and never satisfy a cover clause, so they are
irrelevant as required.  When u = 0 there are no cover clauses; if all sets are
empty (necessarily, since the universe is empty) there are no clauses at all,
and the formula is satisfiable, matching the "u = 0 is yes" edge case.

The number of variables is len(sets) and the number of clauses is at most
u + len(sets)*(len(sets)-1)/2, so the reduction is polynomial.
"""


def reduce(instance):
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    num_sets = len(sets)

    # Bitmask for each set: bit e is set iff element e belongs to the set.
    masks = []
    for subset in sets:
        mask = 0
        for element in subset:
            mask |= 1 << element
        masks.append(mask)

    clauses = []

    # Clause 1: every element must be covered by at least one chosen set.
    for element in range(universe_size):
        bit = 1 << element
        clause = [i + 1 for i in range(num_sets) if masks[i] & bit]
        clauses.append(clause)

    # Clause 2: chosen sets must be pairwise disjoint.
    for i in range(num_sets):
        for j in range(i + 1, num_sets):
            if masks[i] & masks[j]:
                clauses.append([-(i + 1), -(j + 1)])

    return {"num_vars": num_sets, "clauses": clauses}
