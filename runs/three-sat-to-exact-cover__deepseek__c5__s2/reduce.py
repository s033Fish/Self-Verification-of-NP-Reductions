"""Polynomial-time reduction from 3-SAT (ThreeSat) to Exact Cover.

Construction
------------
Let the formula have m variables (1..m) and q clauses.

Universe elements:
  * v_i        for i = 1..m        (variable selectors)
  * c_j        for j = 0..q-1      (one per clause)
  * e_{j,k}    for j = 0..q-1, k=0..2 (one per literal occurrence)

Sets:
  * For each variable i:
      T_i = {v_i} U { e_{j,k} : clause j's k-th literal is -i }   (x_i = true)
      F_i = {v_i} U { e_{j,k} : clause j's k-th literal is +i }   (x_i = false)
    Both contain v_i, so exactly one is chosen; the chosen one covers the
    occurrence elements of the literal that is FALSE.
  * For each clause j and k = 0,1,2:
      {c_j, e_{j,k}}   (use literal k to satisfy the clause)
      {e_{j,k}}        (filler: absorb a true literal not used for c_j)

Correctness: c_j can only be covered by some {c_j, e_{j,k}}, which requires
e_{j,k} not to be covered by a variable set, i.e. literal k is true.  So a
cover exists iff every clause has a true literal under the assignment read
off from the chosen variable sets.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    q = len(clauses)

    # element ids
    # v_i            -> i-1            (i = 1..m)
    # c_j            -> m + j
    # e_{j,k}        -> m + q + 3*j + k
    universe_size = m + q + 3 * q

    pos_occ: dict[int, list[int]] = {i: [] for i in range(1, m + 1)}
    neg_occ: dict[int, list[int]] = {i: [] for i in range(1, m + 1)}

    for j, clause in enumerate(clauses):
        for k, lit in enumerate(clause):
            e = m + q + 3 * j + k
            if lit > 0:
                pos_occ[lit].append(e)
            else:
                neg_occ[-lit].append(e)

    sets: list[list[int]] = []

    # variable gadgets
    for i in range(1, m + 1):
        v = i - 1
        # x_i true  -> negative literal -i is false -> cover its occurrences
        sets.append([v] + neg_occ[i])
        # x_i false -> positive literal +i is false -> cover its occurrences
        sets.append([v] + pos_occ[i])

    # clause gadgets
    for j in range(q):
        c = m + j
        for k in range(3):
            e = m + q + 3 * j + k
            sets.append([c, e])
            sets.append([e])

    return {"universe_size": universe_size, "sets": sets}
