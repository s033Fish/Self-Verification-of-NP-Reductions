"""Polynomial-time reduction from 3-SAT (ThreeSat) to 3-Coloring (ThreeColoring).

Standard gadget reduction.

Target graph layout
-------------------
* Vertices 0, 1, 2 form a triangle: they are the three colours, named
  T (0), F (1) and B (2).  They must receive three distinct colours, so we
  may think of T as "true", F as "false" and B as a neutral "base" colour.
* For every variable v (1..m) there are two vertices:
      pos[v] and neg[v]
  joined by an edge and both joined to B.  Since both are adjacent to B they
  cannot use B's colour, and since they are adjacent to each other they must
  use two different colours; hence exactly one of them gets T and the other
  gets F.  This encodes a truth assignment.
* For every clause (l1 or l2 or l3) there are three fresh vertices forming a
  triangle, with the i-th clause vertex joined to the vertex representing
  literal li.  The clause triangle forces its three vertices to use all three
  colours.  The vertex coloured F must be adjacent to a literal coloured T,
  i.e. a true literal; conversely if some literal is true we can colour the
  clause gadget.  Hence the clause is satisfiable iff the gadget is
  colourable.

The graph has n = 3 + 2*m + 3*len(clauses) vertices and
O(m + len(clauses)) edges, so the construction is polynomial time.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Reduce a 3-SAT instance to a 3-Coloring instance."""
    m = instance["num_vars"]
    clauses = instance["clauses"]

    T, F, B = 0, 1, 2

    # pos[v], neg[v] for v in 1..m
    pos = {}
    neg = {}
    next_vertex = 3
    for v in range(1, m + 1):
        pos[v] = next_vertex
        neg[v] = next_vertex + 1
        next_vertex += 2

    edges = [[T, F], [F, B], [T, B]]

    # Variable gadgets.
    for v in range(1, m + 1):
        edges.append([pos[v], neg[v]])
        edges.append([pos[v], B])
        edges.append([neg[v], B])

    def literal_vertex(literal: int) -> int:
        if literal > 0:
            return pos[literal]
        return neg[-literal]

    # Clause gadgets.
    for clause in clauses:
        a = next_vertex
        b = next_vertex + 1
        c = next_vertex + 2
        next_vertex += 3
        # triangle among the three clause vertices
        edges.append([a, b])
        edges.append([b, c])
        edges.append([a, c])
        # connect each clause vertex to its literal's vertex
        edges.append([a, literal_vertex(clause[0])])
        edges.append([b, literal_vertex(clause[1])])
        edges.append([c, literal_vertex(clause[2])])

    return {"n": next_vertex, "edges": edges}
