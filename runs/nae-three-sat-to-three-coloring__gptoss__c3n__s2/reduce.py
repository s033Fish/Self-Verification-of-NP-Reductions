"""Reduction from NAE-3-SAT to 3-Coloring.

The reduction follows the classic construction (see Garey & Johnson, GT1).
We create a base triangle with vertices representing the three colours
``T`` (true), ``F`` (false) and ``B`` (the third colour).  Every variable
``x`` gets two vertices ``x`` and ``¬x`` which are both adjacent to ``B``
so they cannot be coloured ``B``; an edge between them forces opposite
colours, i.e. one true and one false.

For each clause ``(ℓ1, ℓ2, ℓ3)`` we introduce three new vertices
``c1, c2, c3`` forming a triangle.  Each ``ci`` is connected to the
vertex representing the corresponding literal ``ℓi``.  The clause triangle
must be coloured with three distinct colours.  If the three literals were
all true (or all false) then all three ``ci`` would be forbidden from that
colour and the triangle could not be properly coloured.  Conversely, if the
clause is *not* all‑equal then a proper colouring exists.  Hence the NAE‑3‑SAT
formula is satisfiable iff the constructed graph is 3‑colourable.

The implementation builds the graph as a dict ``{"n": n, "edges": [...]}``
compatible with :class:`ThreeColoring` defined in ``problems.py``.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import NaeThreeSat, ThreeColoring


def _add_edge(edges: set[Tuple[int, int]], u: int, v: int) -> None:
    """Add an undirected edge to the edge set (stored with ordered tuple)."""
    if u == v:
        raise ValueError("self-loops are not allowed")
    edge = (u, v) if u < v else (v, u)
    edges.add(edge)


def reduce(instance: Dict) -> Dict:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dict with keys ``"num_vars"`` and ``"clauses"`` as described in
        :class:`NaeThreeSat`.

    Returns
    -------
    dict
        A graph instance suitable for :class:`ThreeColoring`.
    """
    # Validate the source instance first – this will raise if malformed.
    NaeThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    edges: set[Tuple[int, int]] = set()

    # Base triangle vertices: 0 = T, 1 = F, 2 = B
    T, F, B = 0, 1, 2
    _add_edge(edges, T, F)
    _add_edge(edges, T, B)
    _add_edge(edges, F, B)

    # Offsets for variable vertices.
    # For each variable i (1‑based) we allocate two vertices:
    #   pos_i = base + 2*i - 1   (represents literal +i)
    #   neg_i = base + 2*i       (represents literal -i)
    base_var = 3  # first index after the base triangle
    pos_vertices: List[int] = []  # index i‑1 -> vertex for +i
    neg_vertices: List[int] = []  # index i‑1 -> vertex for -i
    for i in range(1, m + 1):
        pos = base_var + 2 * (i - 1)
        neg = pos + 1
        pos_vertices.append(pos)
        neg_vertices.append(neg)
        # each literal vertex adjacent to B so it cannot take colour B
        _add_edge(edges, pos, B)
        _add_edge(edges, neg, B)
        # opposite literals must have opposite colours
        _add_edge(edges, pos, neg)

    # Clause gadgets
    # For each clause we create three new vertices forming a triangle.
    # They will be placed after all variable vertices.
    next_vertex = base_var + 2 * m
    for clause in clauses:
        # clause vertices c1, c2, c3
        c_vertices = [next_vertex, next_vertex + 1, next_vertex + 2]
        next_vertex += 3
        # triangle among them
        _add_edge(edges, c_vertices[0], c_vertices[1])
        _add_edge(edges, c_vertices[1], c_vertices[2])
        _add_edge(edges, c_vertices[0], c_vertices[2])
        # connect each to the corresponding literal vertex
        for lit, c_vert in zip(clause, c_vertices):
            if lit > 0:
                lit_vertex = pos_vertices[lit - 1]
            else:
                lit_vertex = neg_vertices[abs(lit) - 1]
            _add_edge(edges, lit_vertex, c_vert)

    # Convert edge set to required list format
    edge_list: List[List[int]] = [[u, v] for (u, v) in edges]
    graph_instance = {"n": next_vertex, "edges": edge_list}

    # Validate the target instance before returning.
    ThreeColoring.validate(graph_instance)
    return graph_instance

