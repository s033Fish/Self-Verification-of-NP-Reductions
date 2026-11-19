"""Polynomial-time reduction from Exact Cover to SAT.

Source instance: {"universe_size": u, "sets": [[element, ...], ...]}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce one boolean variable x_i for every set S_i (variable i+1, so
variables are 1..n).  x_i means "set S_i is chosen".

* For every universe element e, add the clause
      OR { x_i : e in S_i }.
  This forces the chosen sets to cover every element (at least once).

* For every pair of sets S_i, S_j (i < j) that share at least one
  element, add the clause
      ( -x_i OR -x_j ).
  This forbids choosing two sets that overlap, so no element is covered
  twice.

Together the clauses say: the chosen sets are pairwise disjoint and
cover the whole universe, i.e. they form an exact cover.  Empty sets
appear in no element clause and overlap nothing, so they are
unconstrained (they never matter).  Two copies of the same non-empty
set share elements, so the corresponding pair clause forbids choosing
both.

Edge cases
----------
* u = 0: there are no element clauses; the pairwise clauses are
  satisfiable by setting every variable false, so the formula is
  satisfiable (choose no sets) -- correct.
* An element not contained in any set yields the empty clause [], which
  is unsatisfiable -- correct (the element cannot be covered).
* No sets at all: num_vars = 0; if u > 0 every element clause is empty
  (unsatisfiable), and if u = 0 the formula has no clauses
  (satisfiable) -- correct.

The construction uses O(u * n + n^2) clauses and runs in polynomial
time.  It never calls a solver.
"""

from collections import defaultdict


def reduce(instance):
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    num_sets = len(sets)

    clauses = []

    # Coverage clauses: every element must be covered by some chosen set.
    # element_to_sets[e] collects the indices of sets containing e.
    element_to_sets = defaultdict(list)
    for i, s in enumerate(sets):
        for e in set(s):
            element_to_sets[e].append(i)

    for e in range(universe_size):
        clauses.append([i + 1 for i in element_to_sets.get(e, [])])

    # Disjointness clauses: overlapping sets cannot both be chosen.
    seen_pairs = set()
    for idxs in element_to_sets.values():
        for a in range(len(idxs)):
            i = idxs[a]
            for b in range(a + 1, len(idxs)):
                j = idxs[b]
                if i == j:
                    continue
                if i < j:
                    key = (i, j)
                else:
                    key = (j, i)
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                clauses.append([-(key[0] + 1), -(key[1] + 1)])

    return {"num_vars": num_sets, "clauses": clauses}
