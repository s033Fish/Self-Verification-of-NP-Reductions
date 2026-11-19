"""Polynomial-time reduction from Exact Cover to SAT.

Exact Cover instance:
    {"universe_size": u, "sets": [[element, ...], ...]}

SAT instance:
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce one Boolean variable x_j for each input set j (variables are
1-based, so set j gets variable j + 1).  Intuitively x_j is true iff set j
is selected.

1. For every universe element e, add the clause

       [j + 1 for every set j containing e]

   This forces at least one selected set to contain e.

2. For every pair of distinct sets i, j that share at least one element,
   add the clause

       [-(i + 1), -(j + 1)]

   This forbids selecting both i and j, i.e. it enforces pairwise
   disjointness of the selected sets.

Together, (1) says the selected sets cover the universe and (2) says they
are pairwise disjoint, so the selected sets are an exact cover.  Conversely
an exact cover satisfies every clause by selecting exactly its sets.

Edge cases
----------
* u = 0: there are no element clauses.  The overlap clauses (if any) are
  satisfiable, e.g. by setting every variable false, so the formula is yes.
* Empty sets: they share no element with any set, so they only introduce
  an unconstrained variable and never affect satisfiability.
* Duplicate non-empty sets: they share elements, so the overlap clause
  prevents choosing both, as required.
* If some element is in no set, its element clause is empty, making the
  formula unsatisfiable, which is correct.

The number of variables is the number of sets, and the number of clauses
is at most u + (number of overlapping set pairs).  Every pair of sets is
considered only through the elements they share, so the running time is
polynomial in the input size.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce an Exact Cover instance to a SAT instance."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    num_sets = len(sets)

    # For each element, the indices of the sets that contain it.
    containing = [[] for _ in range(universe_size)]
    for index, subset in enumerate(sets):
        for element in subset:
            containing[element].append(index)

    clauses = []

    # Coverage clauses: every element must be covered by a selected set.
    for element in range(universe_size):
        clauses.append([index + 1 for index in containing[element]])

    # Disjointness clauses: overlapping sets cannot both be selected.
    seen_pairs = set()
    for element in range(universe_size):
        indices = containing[element]
        for a in range(len(indices)):
            i = indices[a]
            for b in range(a + 1, len(indices)):
                j = indices[b]
                pair = (i, j) if i < j else (j, i)
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                clauses.append([-(i + 1), -(j + 1)])

    return {"num_vars": num_sets, "clauses": clauses}
