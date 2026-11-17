"""Polynomial-time reduction from 3-SAT (ThreeSat) to Exact Cover (ExactCover).

Source instance:  {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Target instance:  {"universe_size": u, "sets": [[element, ...], ...]}

Construction
------------
Universe elements
  * a_i        for each variable i = 1..m      (element index i-1)
  * C_j        for each clause j               (element index m + j)
  * o_{j,k}    for each literal occurrence     (element index m + n + 3*j + k)

Sets
  * For each variable i:
      TRUE_i  = {a_i} u { o_{j,k} : literal at (j,k) is -i }
      FALSE_i = {a_i} u { o_{j,k} : literal at (j,k) is +i }
    a_i must be covered exactly once, so exactly one of TRUE_i / FALSE_i is
    chosen.  Choosing TRUE_i covers all negative occurrences of i (leaving the
    positive ones free) and represents x_i = true; FALSE_i is symmetric.
  * For each occurrence (j,k): a clause set {o_{j,k}, C_j}.
  * For each occurrence (j,k): a dummy set {o_{j,k}}.

Correctness
  * A clause element C_j is covered exactly once, by exactly one clause set
    {o_{j,k}, C_j}.  That set can be chosen only if o_{j,k} is not already
    covered by the variable's chosen set, i.e. only if the literal at (j,k) is
    true.  Hence every clause gets a true literal.
  * Conversely, from a satisfying assignment choose TRUE_i/FALSE_i accordingly,
    one clause set per clause using a true literal, and dummies for the
    remaining true occurrences: this is an exact cover.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict) -> dict:
    """Reduce a 3-SAT instance to an Exact Cover instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    n = len(clauses)

    # Element index layout.
    def a_elem(var: int) -> int:            # var is 1-based
        return var - 1

    def c_elem(j: int) -> int:
        return num_vars + j

    def o_elem(j: int, k: int) -> int:
        return num_vars + n + 3 * j + k

    universe_size = num_vars + 4 * n

    # For each variable, collect occurrence elements of each polarity.
    pos_occ: list[list[int]] = [[] for _ in range(num_vars + 1)]  # 1-based
    neg_occ: list[list[int]] = [[] for _ in range(num_vars + 1)]
    for j, clause in enumerate(clauses):
        for k, literal in enumerate(clause):
            var = abs(literal)
            if literal > 0:
                pos_occ[var].append(o_elem(j, k))
            else:
                neg_occ[var].append(o_elem(j, k))

    sets: list[list[int]] = []

    # Variable choice sets.
    for var in range(1, num_vars + 1):
        a = a_elem(var)
        # TRUE set: covers a and all negative occurrences (positive stay free).
        sets.append([a] + neg_occ[var])
        # FALSE set: covers a and all positive occurrences (negative stay free).
        sets.append([a] + pos_occ[var])

    # Clause sets and dummy sets.
    for j, clause in enumerate(clauses):
        c = c_elem(j)
        for k in range(len(clause)):
            o = o_elem(j, k)
            sets.append([o, c])   # clause set: covers occurrence + clause element
            sets.append([o])      # dummy: can absorb an unused true occurrence

    return {"universe_size": universe_size, "sets": sets}
