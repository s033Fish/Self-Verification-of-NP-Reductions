"""Polynomial-time reduction from 3-SAT to Vertex Cover.

Standard gadget reduction:

* For every variable v in 1..m create two vertices
      T(v) = 2*(v-1)      (represents v = True)
      F(v) = 2*(v-1) + 1  (represents v = False)
  joined by an edge.  Any vertex cover must contain at least one of the two,
  i.e. it must "choose" a truth value for v.

* For every clause c (index j, 0-based) create a triangle of three vertices,
  one per literal:
      base = 2*m + 3*j
      literal vertex for l1 -> base
      literal vertex for l2 -> base + 1
      literal vertex for l3 -> base + 2
  The three triangle edges force at least two of the three vertices into any
  vertex cover.  The one left out corresponds to a literal that must be true
  (the variable vertex representing that literal must be selected).

* k = m + 2*C, where C is the number of clauses.

A cover of size <= k exists iff the formula is satisfiable.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    n_vars = num_vars
    n_clauses = len(clauses)

    def var_true(v: int) -> int:
        return 2 * (v - 1)

    def var_false(v: int) -> int:
        return 2 * (v - 1) + 1

    def literal_vertex(literal: int) -> int:
        v = abs(literal)
        return var_true(v) if literal > 0 else var_false(v)

    edges: list[list[int]] = []

    # Variable gadgets: at least one of {T(v), F(v)} must be in the cover.
    for v in range(1, n_vars + 1):
        edges.append([var_true(v), var_false(v)])

    # Clause gadgets: a triangle per clause; at least two of its vertices
    # must be in the cover.
    for j, clause in enumerate(clauses):
        base = 2 * n_vars + 3 * j
        a, b, c = base, base + 1, base + 2
        edges.append([a, b])
        edges.append([b, c])
        edges.append([a, c])

    n = 2 * n_vars + 3 * n_clauses
    k = n_vars + 2 * n_clauses

    return {"n": n, "edges": edges, "k": k}
