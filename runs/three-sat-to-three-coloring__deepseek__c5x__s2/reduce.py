"""Polynomial-time reduction from 3-SAT to 3-Coloring.

Construction (standard palette/gadget reduction):

  * Palette triangle P0, P1, P2 (mutually adjacent), representing the three
    colours.  We read P0 as "true", P1 as "false" and P2 as "base".
  * Variable gadget for v: two nodes pos_v / neg_v, both adjacent to P2 and
    adjacent to each other.  Hence they get colours in {P0, P1} and are
    different: exactly one of them is "true".
  * Clause gadget for (l1, l2, l3): three new nodes a1, a2, a3 forming a
    triangle, a1 also adjacent to P2, and ai adjacent to the literal node li.
    The gadget is 3-colourable iff at least one li is coloured P0 (true).

The whole graph is 3-colourable iff the formula is satisfiable.
"""

from __future__ import annotations


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges = set()

    def add_edge(u, v):
        if u == v:
            return
        edges.add((u, v) if u < v else (v, u))

    # Palette triangle.
    P0, P1, P2 = 0, 1, 2
    add_edge(P0, P1)
    add_edge(P1, P2)
    add_edge(P0, P2)

    next_id = 3

    # Variable gadgets.
    pos = {}
    neg = {}
    for v in range(1, num_vars + 1):
        pos[v] = next_id
        next_id += 1
        neg[v] = next_id
        next_id += 1
        add_edge(pos[v], neg[v])
        add_edge(pos[v], P2)
        add_edge(neg[v], P2)

    def literal_node(lit):
        return pos[lit] if lit > 0 else neg[-lit]

    # Clause gadgets.
    for clause in clauses:
        a1 = next_id
        a2 = next_id + 1
        a3 = next_id + 2
        next_id += 3
        add_edge(a1, a2)
        add_edge(a2, a3)
        add_edge(a1, a3)
        add_edge(a1, P2)
        add_edge(a1, literal_node(clause[0]))
        add_edge(a2, literal_node(clause[1]))
        add_edge(a3, literal_node(clause[2]))

    n = next_id
    edge_list = [[u, v] for (u, v) in sorted(edges)]
    return {"n": n, "edges": edge_list}
