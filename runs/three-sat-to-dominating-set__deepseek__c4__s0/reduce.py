"""Polynomial-time reduction from 3-SAT (ThreeSat) to Dominating Set.

Source instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Target instance: {"n": n, "edges": [[u, v], ...], "k": k}

Construction
------------
For each variable i in 1..m we build a 4-vertex "truth gadget" with vertices

    T_i (literal +i is true), F_i (literal -i is true), A_i, B_i

and edges

    T_i-F_i, T_i-A_i, T_i-B_i, F_i-A_i, F_i-B_i.

A_i and B_i are non-adjacent twins whose only neighbours are T_i and F_i.
Consequently:
  * any dominating set must contain at least one vertex of the gadget
    (otherwise A_i is undominated), and
  * a single vertex dominates the whole gadget iff it is T_i or F_i
    (A_i misses B_i and vice versa).
So with a budget of exactly one vertex per variable the dominating set must
pick exactly one of T_i / F_i, i.e. a truth value for variable i.

For each clause j we add one vertex z_j, joined to the literal vertex of each
of its three literals (T_i for literal +i, F_i for literal -i).  z_j is
dominated iff at least one of its literal vertices is in the dominating set,
i.e. iff the clause is satisfied by the chosen assignment.

We set k = m.  A satisfying assignment yields a dominating set of size m
(one literal vertex per variable).  Conversely a dominating set of size <= m
must use exactly one vertex per truth gadget (each gadget needs >= 1 and the
gadgets are disjoint), hence no clause vertices, so every z_j must be
dominated by a chosen literal vertex: the assignment satisfies every clause.

The construction uses O(m + c) vertices and edges, so it is polynomial.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to a Dominating Set instance."""
    m = instance["num_vars"]
    clauses = instance["clauses"]

    edges: list[list[int]] = []

    def literal_vertex(literal: int) -> int:
        # Variable i (1-based) occupies vertices 4*(i-1) .. 4*(i-1)+3.
        base = 4 * (abs(literal) - 1)
        return base if literal > 0 else base + 1  # T_i for +i, F_i for -i

    # Truth gadget for every variable 1..m.
    for i in range(m):
        t = 4 * i
        f = t + 1
        a = t + 2
        b = t + 3
        edges.append([t, f])
        edges.append([t, a])
        edges.append([t, b])
        edges.append([f, a])
        edges.append([f, b])

    # One vertex per clause, adjacent to the literal vertices it contains.
    for j, clause in enumerate(clauses):
        z = 4 * m + j
        for literal in clause:
            edges.append([z, literal_vertex(literal)])

    n = 4 * m + len(clauses)
    return {"n": n, "edges": edges, "k": m}
