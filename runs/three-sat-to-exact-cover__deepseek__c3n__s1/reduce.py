"""Polynomial-time reduction from 3-SAT to Exact Cover.

Construction
------------
Given a 3-SAT instance with ``m`` variables (1..m) and ``C`` clauses, build an
Exact Cover instance over the following universe:

  * ``d_i`` for i = 0..m-1        -- one "decision" element per variable.
  * ``c_j`` for j = 0..C-1        -- one element per clause.
  * ``e_{j,k}`` for j = 0..C-1, k = 0..2
                                  -- one element per literal occurrence.

Sets:

  * ``T_i = {d_i} U {e_{j,k} : clause j, position k holds -x_i}``
    (chosen to mean "x_i is true"; it covers the occurrence elements of the
    *negative* occurrences, i.e. the literals that become false).
  * ``F_i = {d_i} U {e_{j,k} : clause j, position k holds +x_i}``
    (chosen to mean "x_i is false").
  * ``{c_j, e_{j,k}}`` for every occurrence (covers clause j using literal k).
  * ``{e_{j,k}}`` for every occurrence (singleton cleanup set).

Exactly one of ``T_i``/``F_i`` is chosen (only they contain ``d_i``), fixing a
truth assignment.  ``c_j`` can only be covered by a clause set ``{c_j,e_{j,k}}``,
which is usable exactly when the occurrence ``e_{j,k}`` was *not* already
covered by the chosen variable set, i.e. exactly when literal ``k`` is true.
Hence a cover exists iff every clause has a true literal.  All remaining
occurrence elements are absorbed by the singletons.

The construction is linear in the input size, hence polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict) -> dict:
    """Reduce a 3-SAT instance to an Exact Cover instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    # Element layout.
    d_base = 0
    c_base = num_vars
    e_base = num_vars + num_clauses

    def d(i: int) -> int:
        return d_base + i

    def c(j: int) -> int:
        return c_base + j

    def e(j: int, k: int) -> int:
        return e_base + 3 * j + k

    universe_size = num_vars + 4 * num_clauses
    sets: list[list[int]] = []

    # Variable gadget: T_i (x_i true) and F_i (x_i false).
    for i in range(num_vars):
        var = i + 1
        t_set = [d(i)]
        f_set = [d(i)]
        for j, clause in enumerate(clauses):
            for k, literal in enumerate(clause):
                if literal == -var:
                    t_set.append(e(j, k))
                elif literal == var:
                    f_set.append(e(j, k))
        sets.append(t_set)
        sets.append(f_set)

    # Clause gadget + cleanup singletons.
    for j, clause in enumerate(clauses):
        for k in range(len(clause)):
            sets.append([c(j), e(j, k)])
            sets.append([e(j, k)])

    return {"universe_size": universe_size, "sets": sets}
