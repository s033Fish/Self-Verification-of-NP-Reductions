"""Polynomial-time reduction from 3-SAT (ThreeSat) to Dominating Set.

Construction (n = num_vars, m = number of clauses):

* Variable gadget: for variable v in 1..n add an edge between
  ``T(v) = 2*(v-1)`` and ``F(v) = 2*(v-1)+1``.  Selecting ``T(v)`` means
  v is true, selecting ``F(v)`` means v is false.  Because ``T(v)`` and
  ``F(v)`` are adjacent only to each other, every dominating set must
  contain at least one of them.

* Clause gadget: for each clause add one fresh vertex ``c_j`` and connect
  it to the variable-gadget vertex that makes each of its literals true
  (``T(|l|)`` if ``l > 0`` else ``F(|l|)``).

* Set ``k = n``.

Correctness.  A satisfying assignment yields a dominating set of size n:
pick the true vertex of every variable gadget; every clause vertex is
adjacent to a true literal vertex.  Conversely, any dominating set D with
|D| <= n must contain at least one endpoint of each of the n disjoint
variable edges, hence |D| = n and D contains exactly one endpoint per
variable.  That choice is a consistent assignment, and since no clause
vertex is in D, every clause vertex must be adjacent to a chosen literal
vertex, i.e. every clause has a true literal.  So the formula is
satisfiable.  The construction is linear in the input size.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    def true_vertex(var: int) -> int:
        return 2 * (var - 1)

    def false_vertex(var: int) -> int:
        return 2 * (var - 1) + 1

    n = 2 * num_vars
    edges: list[list[int]] = []

    # Variable gadgets.
    for var in range(1, num_vars + 1):
        edges.append([true_vertex(var), false_vertex(var)])

    # Clause gadgets: one vertex per clause attached to its literal vertices.
    for clause in clauses:
        node = n
        n += 1
        for literal in clause:
            var = abs(literal)
            edges.append([node, true_vertex(var) if literal > 0 else false_vertex(var)])

    k = num_vars
    return {"n": n, "edges": edges, "k": k}
