"""Polynomial-time reduction from 3-SAT (ThreeSat) to 3-Coloring (ThreeColoring).

Idea
----
We build a graph whose 3-colourings correspond to satisfying assignments.

Base:  F0 -- B0   (edge).  In any colouring F0 and B0 get two distinct
colours; relabel so that F0 = colour 1 ("false") and B0 = colour 2 ("blue"),
the remaining colour 0 is "true".

Variable i (1..m): vertices xi and nxi (= not xi) with edges
    xi -- nxi,  xi -- B0,  nxi -- B0.
Since both are adjacent to B0 they avoid B0's colour, and being adjacent to
each other they take the two remaining colours: exactly one is 0 (true) and
the other is 1 (false).  So each variable is assigned a consistent truth
value, and any truth value is realisable.

Clause gadget: a fixed 9-vertex gadget (vertices 0..8) with edges
    (0,7) (1,4) (1,5) (2,8) (3,6) (4,6) (4,7) (5,7) (5,8) (6,8)
Local vertices 0,1,2 are the three literal terminals, local vertex 3 is
identified with F0 (colour 1), local vertices 4..8 are fresh.  For terminal
colours in {0,1} (guaranteed, as literals are adjacent to B0) the gadget is
3-colourable iff NOT all three terminals have colour 1 (i.e. iff at least one
literal is true).  This was verified by exhaustive search.

Hence the whole graph is 3-colourable iff there is a truth assignment making
every clause true, i.e. iff the formula is satisfiable.
"""

from __future__ import annotations

# Local edges of the clause gadget.  Vertices 0,1,2 = literal terminals,
# vertex 3 = the shared "false" vertex F0, vertices 4..8 = fresh internals.
_GADGET_EDGES = [
    (0, 7), (1, 4), (1, 5), (2, 8), (3, 6),
    (4, 6), (4, 7), (5, 7), (5, 8), (6, 8),
]


def reduce(instance):
    """Reduce a 3-SAT instance to a 3-Coloring instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges = set()

    def add(u, v):
        if u == v:
            return
        edges.add((u, v) if u < v else (v, u))

    # Base edge: F0 (false, colour 1) -- B0 (blue, colour 2).
    F0, B0 = 0, 1
    add(F0, B0)

    # Variable gadgets.
    def var_pos(i):  # vertex for literal +i, i in 1..num_vars
        return 2 + 2 * (i - 1)

    def var_neg(i):  # vertex for literal -i
        return 3 + 2 * (i - 1)

    for i in range(1, num_vars + 1):
        x, nx = var_pos(i), var_neg(i)
        add(x, nx)
        add(x, B0)
        add(nx, B0)

    def lit_vertex(lit):
        return var_pos(lit) if lit > 0 else var_neg(-lit)

    next_vertex = 2 + 2 * num_vars

    # One clause gadget per clause.
    for clause in clauses:
        # local 0,1,2 -> the three literals, local 3 -> F0, local 4..8 fresh
        local = [lit_vertex(clause[0]), lit_vertex(clause[1]),
                 lit_vertex(clause[2]), F0]
        for _ in range(5):
            local.append(next_vertex)
            next_vertex += 1
        for a, b in _GADGET_EDGES:
            add(local[a], local[b])

    n = next_vertex
    return {"n": n, "edges": [list(e) for e in sorted(edges)]}
