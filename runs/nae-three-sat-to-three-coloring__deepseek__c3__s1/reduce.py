"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Construction (standard gadget reduction)
----------------------------------------
Use three colours, which we name T, F and B (base).

* A triangle on three special vertices B, T, F forces them to receive the
  three distinct colours.  We read the colour of T as "true" and the colour
  of F as "false"; B is the neutral base colour.

* For every variable v (1..m) add two vertices pos(v) and neg(v).  Both are
  joined to B and to each other.  Hence neither can take colour B, and they
  must differ, so one is coloured T and the other F: this encodes an
  assignment of v.

* For every clause (l1, l2, l3) add three fresh vertices forming a triangle,
  and join the i-th of them to the literal vertex of li (pos(v) for +v,
  neg(v) for -v).

A clause triangle can be coloured (avoiding its three literal colours) iff
the three literals are not all the same colour.  Indeed, if all three
literals share a colour, the triangle vertices may only use the other two
colours, impossible for a triangle; otherwise, if the literal colours are
T,T,F (up to symmetry) we may colour the triangle vertices F,B,T.

Therefore the graph is 3-colourable iff the formula has a not-all-equal
satisfying assignment.  The graph has 3 + 2*m + 3*(#clauses) vertices and
3 + 3*m + 6*(#clauses) edges, so the reduction runs in polynomial time.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Map a NAE-3-SAT instance to a 3-Coloring instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges: list[list[int]] = []
    seen: set[frozenset[int]] = set()

    def add_edge(u: int, v: int) -> None:
        key = frozenset((u, v))
        if key not in seen:
            seen.add(key)
            edges.append([u, v])

    # Special triangle B, T, F.
    base, true_v, false_v = 0, 1, 2
    add_edge(base, true_v)
    add_edge(base, false_v)
    add_edge(true_v, false_v)

    next_vertex = 3

    # Variable gadgets: pos(v) and neg(v), both joined to base and each other.
    pos = {}
    neg = {}
    for v in range(1, num_vars + 1):
        p = next_vertex
        n = next_vertex + 1
        next_vertex += 2
        pos[v] = p
        neg[v] = n
        add_edge(p, n)
        add_edge(p, base)
        add_edge(n, base)

    # Clause gadgets: a fresh triangle, one vertex attached to each literal.
    for clause in clauses:
        c0 = next_vertex
        c1 = next_vertex + 1
        c2 = next_vertex + 2
        next_vertex += 3
        add_edge(c0, c1)
        add_edge(c1, c2)
        add_edge(c0, c2)
        for gadget_vertex, literal in zip((c0, c1, c2), clause):
            variable = abs(literal)
            literal_vertex = pos[variable] if literal > 0 else neg[variable]
            add_edge(gadget_vertex, literal_vertex)

    return {"n": next_vertex, "edges": edges}
