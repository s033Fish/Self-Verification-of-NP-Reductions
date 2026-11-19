"""Polynomial-time reduction from 3-SAT to 3-Coloring.

Construction
------------
Three base vertices form a triangle and act as the three colours:

    0 = TRUE, 1 = FALSE, 2 = BASE

For every variable v we add two vertices x_v and ~x_v, join them to each
other and to BASE.  Hence x_v and ~x_v always receive TRUE/FALSE and are
opposite, so a 3-colouring encodes a truth assignment.

Clause gadget
-------------
An OR gate on inputs u, v (each TRUE or FALSE) is the triangle (a, b, c)
with edges a-u, b-v and c-BASE.  c is never BASE.  If u = v = FALSE then
a, b must be TRUE and BASE in some order, forcing c = FALSE.  If at least
one input is TRUE, c can be coloured TRUE (and also FALSE).  Thus c can be
TRUE exactly when u or v is TRUE.

For a clause (l1, l2, l3) we chain two OR gates:

    c1 = OR(l1, l2)          c2 = OR(c1, l3)

and force c2 = TRUE by joining it to FALSE and BASE.  The gadget is
3-colourable exactly when at least one of l1, l2, l3 is TRUE.  The
gadgets for different clauses are vertex-disjoint, so the whole graph is
3-colourable iff the formula is satisfiable.

The graph has 3 + 2*m + 6*k vertices and O(m + k) edges, where k is the
number of clauses, so the reduction is polynomial.
"""

from typing import Any, Dict, List


def _literal_vertex(literal: int) -> int:
    """Vertex encoding a literal. Variables are 1-based."""
    base = 3 + 2 * (abs(literal) - 1)
    return base if literal > 0 else base + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Be robust to literals that reference variables beyond num_vars.
    max_var = num_vars
    for clause in clauses:
        for literal in clause:
            if abs(literal) > max_var:
                max_var = abs(literal)

    TRUE, FALSE, BASE = 0, 1, 2

    edges: List[List[int]] = []
    seen = set()

    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        key = (u, v) if u < v else (v, u)
        if key not in seen:
            seen.add(key)
            edges.append([u, v])

    # Base triangle: three distinct colours.
    add_edge(TRUE, FALSE)
    add_edge(FALSE, BASE)
    add_edge(TRUE, BASE)

    # Variable vertices: x_v and ~x_v opposite, both different from BASE.
    for v in range(1, max_var + 1):
        pos = 3 + 2 * (v - 1)
        neg = pos + 1
        add_edge(pos, neg)
        add_edge(pos, BASE)
        add_edge(neg, BASE)

    n = 3 + 2 * max_var

    # Clause gadgets.
    for clause in clauses:
        l1, l2, l3 = clause
        a1, b1, c1, a2, b2, c2 = range(n, n + 6)
        n += 6

        # First OR gate: c1 = OR(l1, l2)
        add_edge(a1, b1)
        add_edge(b1, c1)
        add_edge(a1, c1)
        add_edge(a1, _literal_vertex(l1))
        add_edge(b1, _literal_vertex(l2))
        add_edge(c1, BASE)

        # Second OR gate: c2 = OR(c1, l3)
        add_edge(a2, b2)
        add_edge(b2, c2)
        add_edge(a2, c2)
        add_edge(a2, c1)
        add_edge(b2, _literal_vertex(l3))
        add_edge(c2, BASE)

        # Force c2 = TRUE.
        add_edge(c2, FALSE)
        add_edge(c2, BASE)

    return {"n": n, "edges": edges}
