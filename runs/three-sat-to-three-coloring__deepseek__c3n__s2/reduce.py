"""Polynomial-time reduction from 3-SAT to 3-Coloring.

Idea
----
Fix a base triangle of three vertices T, F, B that receive the three distinct
colours.  We read the colour of T as "true" and the colour of F as "false".

Variable gadget: for each variable v we add vertices v and ~v, connect them to
each other and both to B.  Hence v and ~v must take the two colours different
from B's colour, i.e. exactly one of them is "true" and the other "false".

Clause gadget: three fresh vertices a,b,c forming a triangle, with a,b,c
connected to three "input" vertices x1,x2,x3 whose colours are already fixed
to true/false.  The gadget is 3-colourable iff x1,x2,x3 are NOT all equal:
  * if all three inputs share a colour, a,b,c must avoid that colour and a
    triangle cannot be coloured with only two colours;
  * otherwise a valid permutation of the three colours avoiding the three
    forbidden colours always exists.

A clause (l1 v l2 v l3) is satisfiable iff there is a value of a fresh
variable z with NAE(l1,l2,z) and NAE(~z,l3,F), where F is the constant-false
base vertex.  So each clause becomes two triangle gadgets (plus the fresh
variable z), which is a correct, polynomial reduction.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Base triangle: T = true colour, F = false colour, B = base colour.
    T, F, B = 0, 1, 2
    edges: list[list[int]] = [[T, F], [F, B], [B, T]]
    n = 3

    def new_node() -> int:
        nonlocal n
        node = n
        n += 1
        return node

    # Variable gadgets.
    pos: dict[int, int] = {}
    neg: dict[int, int] = {}
    for v in range(1, num_vars + 1):
        p = new_node()
        q = new_node()
        pos[v] = p
        neg[v] = q
        edges.append([p, q])
        edges.append([p, B])
        edges.append([q, B])

    def lit_node(lit: int) -> int:
        if lit > 0:
            return pos[lit]
        return neg[-lit]

    def add_nae_gadget(x1: int, x2: int, x3: int) -> None:
        """Triangle gadget: colourable iff x1, x2, x3 are not all equal."""
        a = new_node()
        b = new_node()
        c = new_node()
        edges.append([a, b])
        edges.append([b, c])
        edges.append([c, a])
        edges.append([a, x1])
        edges.append([b, x2])
        edges.append([c, x3])

    for clause in clauses:
        l1, l2, l3 = clause
        # Fresh variable z for this clause.
        zp = new_node()
        zn = new_node()
        edges.append([zp, zn])
        edges.append([zp, B])
        edges.append([zn, B])
        # NAE(l1, l2, z)
        add_nae_gadget(lit_node(l1), lit_node(l2), zp)
        # NAE(~z, l3, F)
        add_nae_gadget(zn, lit_node(l3), F)

    # Safety: remove any duplicate undirected edges (none expected).
    seen: set[tuple[int, int]] = set()
    final_edges: list[list[int]] = []
    for u, v in edges:
        key = (u, v) if u < v else (v, u)
        if key not in seen:
            seen.add(key)
            final_edges.append([u, v])

    return {"n": n, "edges": final_edges}
