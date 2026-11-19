"""Reduction from 3‑SAT to 3‑Coloring.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with the
instance format:

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal is a string ``"+v"`` (variable *v* true) or ``"-v"``
(variable *v* false).  Every clause contains exactly three literals on three
distinct variables.

The target problem is ``ThreeColoring`` with the instance format:

    {"n": n, "edges": [[u, v], ...]}

Vertices are numbered ``0 .. n‑1`` and edges are undirected.

The reduction implements the classic polynomial‑time construction that
creates a graph which is 3‑colorable iff the original formula is satisfiable.

Construction details
----------------------
* Three special vertices form a triangle.  Their colours represent the three
  logical colours used in the reduction: ``TRUE``, ``FALSE`` and ``BASE``.
  We fix the indices ``0`` (TRUE), ``1`` (FALSE) and ``2`` (BASE).

* For each variable *i* (1‑based) we create two vertices ``v_i_T`` and
  ``v_i_F``.  The edges ``(v_i_T, v_i_F)``, ``(v_i_T, FALSE)`` and
  ``(v_i_F, TRUE)`` force the two vertices to receive opposite colours –
  exactly one of them gets the colour ``TRUE`` and the other gets ``FALSE``.
  The vertex ``v_i_T`` represents the literal ``+i`` and ``v_i_F`` the literal
  ``‑i``.

* For every clause ``(ℓ1 ∨ ℓ2 ∨ ℓ3)`` we introduce three new vertices
  ``c_j_0, c_j_1, c_j_2`` that form a triangle.  Vertex ``c_j_k`` is connected
  to the literal vertex that corresponds to ``ℓ{k+1}``.  The triangle must be
  coloured with three distinct colours.  If a literal vertex is coloured
  ``TRUE`` then its adjacent clause‑vertex cannot be coloured ``TRUE`` – it may
  use either ``FALSE`` or ``BASE``.  Conversely, if the literal vertex is
  coloured ``FALSE`` the clause‑vertex cannot be ``FALSE``.  Consequently, a
  clause can be coloured only when at least one of its literals is assigned
  ``TRUE``; otherwise the three clause‑vertices would be forced to use only the
  two colours ``TRUE`` and ``BASE`` (or ``FALSE`` and ``BASE``), which is
  impossible for a triangle.  Hence the graph is 3‑colourable exactly when the
  formula is satisfiable.

The implementation builds the edge set while avoiding duplicates, computes the
total number of vertices, and returns the required dictionary.
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        lists of three literals as strings).

    Returns
    -------
    dict
        A graph instance for ``ThreeColoring`` with keys ``"n"`` and
        ``"edges"``.
    """

    m: int = instance["num_vars"]
    clauses: List[List[str]] = instance["clauses"]

    # Fixed vertices for the colour triangle.
    TRUE = 0
    FALSE = 1
    BASE = 2
    next_vertex = 3  # next free index after the three fixed vertices.

    # Helper to add edges to a set without duplication.
    edges: Set[Tuple[int, int]] = set()

    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        if u > v:
            u, v = v, u
        edges.add((u, v))

    # Triangle among the three colour vertices.
    add_edge(TRUE, FALSE)
    add_edge(FALSE, BASE)
    add_edge(TRUE, BASE)

    # Mapping from (var, polarity) to the vertex representing that literal.
    # polarity == True for positive literal (+v), False for negative (‑v).
    literal_vertex: Dict[Tuple[int, bool], int] = {}

    # Variable gadgets.
    for var in range(1, m + 1):
        v_true = next_vertex
        v_false = next_vertex + 1
        next_vertex += 2
        literal_vertex[(var, True)] = v_true
        literal_vertex[(var, False)] = v_false

        # Force opposite colours.
        add_edge(v_true, v_false)
        add_edge(v_true, FALSE)   # true literal cannot be FALSE colour
        add_edge(v_false, TRUE)   # false literal cannot be TRUE colour

    # Clause gadgets.
    for clause in clauses:
        # clause is a list of three literals like '+3' or '-2'
        # Create three vertices forming a triangle.
        clause_vertices = [next_vertex, next_vertex + 1, next_vertex + 2]
        next_vertex += 3

        # Connect the three clause vertices as a triangle.
        add_edge(clause_vertices[0], clause_vertices[1])
        add_edge(clause_vertices[1], clause_vertices[2])
        add_edge(clause_vertices[2], clause_vertices[0])

        # Connect each clause vertex to the corresponding literal vertex.
        for lit_str, cv in zip(clause, clause_vertices):
            sign = lit_str[0]
            var = int(lit_str[1:])
            # Positive literal maps to the "true" vertex, negative to "false".
            lit_vertex = literal_vertex[(var, sign == '+')]
            add_edge(cv, lit_vertex)

    # Build the output structure.
    edge_list: List[List[int]] = [[u, v] for (u, v) in edges]
    return {"n": next_vertex, "edges": edge_list}

