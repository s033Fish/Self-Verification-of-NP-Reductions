"""Reduction from 3‑SAT to 3‑Coloring.

The construction uses three special vertices representing the colours TRUE (0),
FALSE (1) and BASE (2).  Each variable gets two vertices (positive and
negative literal) that are adjacent to each other and to BASE, forcing them to
receive opposite colours TRUE/FALSE.

For each clause we create a triangle of three new vertices.  Each vertex of the
clause triangle is connected to the vertex of the literal it represents.  If a
clause is unsatisfied (all its literals are FALSE) then every clause vertex is
adjacent to a FALSE‑coloured vertex and therefore cannot use the colour FALSE.
Only the colours TRUE and BASE would remain, which is insufficient for a
triangle, so the graph would not be 3‑colourable.  Conversely, if at least one
literal in the clause is TRUE, the corresponding clause vertex may take the
colour FALSE, allowing a proper 3‑colouring of the triangle.  This is the
standard polynomial‑time reduction from 3‑SAT to 3‑Coloring.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import ThreeSat, ThreeColoring


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        Dictionary with keys ``"num_vars"`` and ``"clauses"`` as defined by
        :class:`ThreeSat`.

    Returns
    -------
    dict
        Graph instance suitable for :class:`ThreeColoring`.
    """
    # Validate source instance.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Special colour vertices.
    TRUE = 0
    FALSE = 1
    BASE = 2
    edges: List[Tuple[int, int]] = []

    # Triangle among the three special vertices.
    edges.extend([(TRUE, FALSE), (FALSE, BASE), (BASE, TRUE)])

    next_id = 3  # next free vertex identifier
    pos_vertex: Dict[int, int] = {}
    neg_vertex: Dict[int, int] = {}

    # Variable gadgets.
    for var in range(1, m + 1):
        pos = next_id
        neg = next_id + 1
        next_id += 2
        pos_vertex[var] = pos
        neg_vertex[var] = neg
        # literals are adjacent (must get opposite colours)
        edges.append((pos, neg))
        # each literal adjacent to BASE (cannot take BASE colour)
        edges.append((pos, BASE))
        edges.append((neg, BASE))

    # Clause gadgets.
    for clause in clauses:
        # three vertices forming a triangle
        c1 = next_id
        c2 = next_id + 1
        c3 = next_id + 2
        next_id += 3
        # triangle edges
        edges.append((c1, c2))
        edges.append((c2, c3))
        edges.append((c1, c3))
        # connect clause vertices to their corresponding literal vertices
        clause_vertices = [c1, c2, c3]
        for lit, cv in zip(clause, clause_vertices):
            var = abs(lit)
            lit_vertex = pos_vertex[var] if lit > 0 else neg_vertex[var]
            edges.append((cv, lit_vertex))

    graph_instance: Dict = {"n": next_id, "edges": [list(e) for e in edges]}
    # Validate target instance (helps catch bugs).
    ThreeColoring.validate(graph_instance)
    return graph_instance

