"""Polynomial-time reduction from Exact Cover to SAT (CNF).

Construction
------------
Given an Exact Cover instance with universe 0..u-1 and sets S_0..S_{n-1},
introduce one boolean variable x_i for each set S_i, meaning "S_i is chosen".

We need:
  * every element is covered by at least one chosen set, and
  * no two chosen sets share an element (pairwise disjointness).

For each element e:
  * "at least one" clause:  (x_i1 or x_i2 or ... or x_ik), over all sets
    containing e.  If no set contains e, this is the empty clause [], which
    is unsatisfiable, correctly making the instance no.
  * "at most one" clauses: for every pair i < j of distinct sets containing
    e, add (-x_i or -x_j).  (Two copies of the same set are distinct indices
    and share e, so they cannot both be chosen.)

The number of variables is n and the number of clauses is at most
u + sum_e C(k_e, 2), which is polynomial in the input size.

Correctness
-----------
A satisfying assignment selects a set of indices whose variables are true.
The at-least-one clauses make the union cover the universe; the at-most-one
clauses make the selected sets pairwise disjoint.  Hence they form an exact
cover.  Conversely, any exact cover yields a satisfying assignment by setting
exactly the chosen sets' variables true (all other variables false), and the
empty-set / duplicate-set / u = 0 edge cases are handled naturally.
"""


def reduce(instance):
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    num_sets = len(sets)

    # sets_containing[e] = list of indices of sets that contain element e.
    sets_containing = [[] for _ in range(universe_size)]
    for i, s in enumerate(sets):
        for e in s:
            sets_containing[e].append(i)

    clauses = []
    for e in range(universe_size):
        containing = sets_containing[e]

        # At least one chosen set covers e.  Empty list => empty clause.
        clauses.append([i + 1 for i in containing])

        # At most one chosen set covers e.
        k = len(containing)
        for a in range(k):
            for b in range(a + 1, k):
                clauses.append([-(containing[a] + 1), -(containing[b] + 1)])

    return {"num_vars": num_sets, "clauses": clauses}
