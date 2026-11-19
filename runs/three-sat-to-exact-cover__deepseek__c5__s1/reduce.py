"""Polynomial-time reduction from 3-SAT (ThreeSat) to Exact Cover (ExactCover).

Construction
------------
Let the 3-SAT instance have variables x_1..x_m and clauses C_1..C_n.

Universe elements:
  * d_i            for each variable i = 1..m
  * c_j            for each clause j = 1..n
  * o_{j,k}        for each clause j and literal position k (0-based)

Variable gadget: two sets sharing d_i
  * T_i = {d_i} U {o_{j,k} : the k-th literal of clause j is -x_i}
  * F_i = {d_i} U {o_{j,k} : the k-th literal of clause j is +x_i}
Choosing T_i means x_i = true, F_i means x_i = false.  Since T_i and F_i
share d_i, at most one is chosen; since d_i must be covered, exactly one is.
When x_i is true, the occurrence elements of the *false* literal -x_i are
covered; the occurrence elements of the *true* literal +x_i stay uncovered
(and vice versa).

Clause gadget: for each clause j and position k
  * {c_j, o_{j,k}}   (use this literal to satisfy the clause)
  * {o_{j,k}}        (dummy: absorb an unused true occurrence)

c_j can only be covered by a clause set {c_j, o_{j,k}} whose o_{j,k} is not
already covered by a variable set, i.e. by a literal that is TRUE.  Every
other occurrence element is covered either by its variable set (false
literal) or by its dummy set (true literal not selected).  Hence an exact
cover exists iff every clause has at least one true literal.

The instance is polynomial in size: m + 4n elements and 2m + 6n sets.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to an Exact Cover instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    m = num_vars
    n = len(clauses)

    # Element index layout.
    #   d_i     -> i - 1                    (i = 1..m)
    #   c_j     -> m + j                    (j = 0..n-1)
    #   o_{j,k} -> m + n + 3*j + k          (j = 0..n-1, k = 0..2)
    def occ(j: int, k: int) -> int:
        return m + n + 3 * j + k

    universe_size = m + n + 3 * n

    sets: list[list[int]] = []

    # Variable gadgets.
    for i in range(1, m + 1):
        d = i - 1
        true_set = [d]   # x_i = true  -> covers false occurrences (-x_i)
        false_set = [d]  # x_i = false -> covers false occurrences (+x_i)
        for j, clause in enumerate(clauses):
            for k, literal in enumerate(clause):
                if abs(literal) == i:
                    if literal < 0:
                        true_set.append(occ(j, k))
                    else:
                        false_set.append(occ(j, k))
        sets.append(true_set)
        sets.append(false_set)

    # Clause gadgets.
    for j, clause in enumerate(clauses):
        c = m + j
        for k in range(len(clause)):
            o = occ(j, k)
            sets.append([c, o])  # satisfy clause j using literal k
            sets.append([o])     # dummy for an unused true occurrence

    return {"universe_size": universe_size, "sets": sets}
