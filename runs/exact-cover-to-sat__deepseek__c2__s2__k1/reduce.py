"""Polynomial-time reduction from Exact Cover to SAT.

Source (Exact Cover):
    {"universe_size": u, "sets": [[element, ...], ...]}
Target (SAT):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce one boolean variable x_i for every input set i (1-indexed).

* For every universe element e, add the clause
      [x_i for every set i containing e].
  This forces each element to be covered by at least one chosen set.

* For every pair of distinct sets i < j that share at least one element,
  add the clause [-x_i, -x_j].
  This forbids choosing two sets that overlap, i.e. it enforces pairwise
  disjointness of the chosen sets.

A satisfying assignment therefore selects a pairwise-disjoint family of
sets whose union is the whole universe, i.e. an exact cover.  Conversely,
any exact cover yields a satisfying assignment by setting x_i true exactly
for the chosen sets.

Edge cases:
* u = 0: there are no coverage clauses, so the formula is trivially
  satisfiable (choose no sets), matching the source semantics.
* Empty sets: they occur in no coverage clause and intersect nothing, so
  their variables are unconstrained; they can always be set false.
* Duplicate non-empty sets: duplicates intersect, so the disjointness
  clause between them forbids choosing both.
* If some element belongs to no set, its coverage clause is empty and the
  formula is unsatisfiable, as required.

The construction uses O(u * n + n^2) time and clauses, where n is the
number of sets, hence it runs in polynomial time.
"""


def reduce(instance):
    """Reduce an Exact Cover instance to a SAT (CNF) instance."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)

    # Bitmask for each set: bit e is set iff element e belongs to the set.
    set_masks = []
    for subset in sets:
        mask = 0
        for element in subset:
            mask |= 1 << element
        set_masks.append(mask)

    clauses = []

    # Coverage: every element must be covered by at least one chosen set.
    for element in range(universe_size):
        bit = 1 << element
        clause = [i + 1 for i, mask in enumerate(set_masks) if mask & bit]
        clauses.append(clause)

    # Disjointness: overlapping sets cannot both be chosen.
    for i in range(n):
        mask_i = set_masks[i]
        for j in range(i + 1, n):
            if mask_i & set_masks[j]:
                clauses.append([-(i + 1), -(j + 1)])

    return {"num_vars": n, "clauses": clauses}
