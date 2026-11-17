"""Reduction from 3‑SAT to 3‑Coloring.

The construction is the classic polynomial‑time reduction:
* Create three special vertices forming a triangle: TRUE (0), FALSE (1), BASE (2).
* For each variable x_i create two vertices pos_i and neg_i, both adjacent to
  BASE and to each other.  This forces them to receive opposite colours, i.e.
  one gets the colour of TRUE and the other the colour of FALSE.
* For each clause (ℓ1 ∨ ℓ2 ∨ ℓ3) create three vertices forming a triangle.
  Vertex j of the clause triangle is connected to the literal vertex that
  corresponds to ℓj.  No edge to BASE is added.

A proper 3‑colouring exists iff the original formula is satisfiable.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import ThreeSat, ThreeColoring


def _add_edge(edges: set[Tuple[int, int]], u: int, v: int) -> None:
    """Add an undirected edge {u, v} to the set, storing it as (min, max)."""
    if u == v:
        raise ValueError("self‑loops are not allowed")
    a, b = (u, v) if u < v else (v, u)
    edges.add((a, b))


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance: dict
        Must conform to ``ThreeSat`` (validated inside).

    Returns
    -------
    dict
        Graph instance for ``ThreeColoring``.
    """
    # Validate source instance.
    ThreeSat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    edges: set[Tuple[int, int]] = set()

    # Special triangle vertices: 0 = TRUE, 1 = FALSE, 2 = BASE
    TRUE, FALSE, BASE = 0, 1, 2
    _add_edge(edges, TRUE, FALSE)
    _add_edge(edges, TRUE, BASE)
    _add_edge(edges, FALSE, BASE)

    # Map each literal (signed int) to its vertex index.
    lit_to_vertex: dict[int, int] = {}
    next_vertex = 3
    for i in range(1, num_vars + 1):
        pos = next_vertex
        neg = next_vertex + 1
        next_vertex += 2
        lit_to_vertex[i] = pos
        lit_to_vertex[-i] = neg
        # Variable gadget edges
        _add_edge(edges, pos, neg)      # opposite colours
        _add_edge(edges, pos, BASE)     # cannot use BASE colour
        _add_edge(edges, neg, BASE)

    # Clause gadgets
    for clause in clauses:
        # Create three vertices for the clause triangle
        clause_vertices: List[int] = []
        for _ in range(3):
            v = next_vertex
            next_vertex += 1
            clause_vertices.append(v)
        a, b, c = clause_vertices
        _add_edge(edges, a, b)
        _add_edge(edges, b, c)
        _add_edge(edges, c, a)
        # Connect each clause vertex to the literal it represents
        for lit, cv in zip(clause, clause_vertices):
            lit_vertex = lit_to_vertex[lit]
            _add_edge(edges, cv, lit_vertex)

    n = next_vertex
    edge_list: List[List[int]] = [[u, v] for (u, v) in edges]
    result = {"n": n, "edges": edge_list}
    # Validate target instance.
    ThreeColoring.validate(result)
    return result

