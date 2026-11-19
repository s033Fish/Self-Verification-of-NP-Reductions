"""Reduction from 3‑SAT to 3‑Coloring.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with the
instance format ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.  A literal
is an integer with sign: ``+v`` (positive) means the variable *v* should be
true, ``-v`` means it should be false.

The target problem is ``ThreeColoring`` with the instance format
``{"n": n, "edges": [[u, v], ...]}``.  Vertices are numbered ``0..n‑1`` and the
edges are undirected.

The classic polynomial‑time reduction constructs a graph that can be coloured
with three colours (we call them **T** (true), **F** (false) and **B** (base))
iff the SAT formula is satisfiable.

Construction
=============

* Create three special vertices ``T = 0``, ``F = 1`` and ``B = 2`` and connect
  them to form a triangle.  This forces any proper 3‑colouring to assign three
  distinct colours to these vertices.

* For each variable ``x_i`` (``i`` from ``1`` to ``m``) create two vertices:
  ``pos_i`` representing the literal ``+i`` and ``neg_i`` representing ``-i``.
  Connect each of them to ``B`` (so they cannot take the base colour) and add
  an edge between ``pos_i`` and ``neg_i``.  In any proper 3‑colouring the two
  vertices must receive the colours of ``T`` and ``F`` in opposite order,
  which corresponds to setting the variable true or false.

* For each clause ``(l1 ∨ l2 ∨ l3)`` create three new vertices forming a
  triangle (the *clause gadget*).  Connect each clause‑vertex to the vertex
  representing the corresponding literal.  If all three literals are coloured
  ``F`` (i.e., the clause is unsatisfied) then each clause‑vertex is forced to
  avoid colour ``F``; only the two remaining colours are available for three
  mutually adjacent vertices – impossible.  Hence the clause gadget can be
  coloured exactly when at least one literal of the clause receives colour
  ``T``.

The resulting graph has ``n = 3 + 2*m + 3*|clauses|`` vertices and a number of
edges linear in the size of the formula, thus the reduction runs in polynomial
time.

The ``reduce`` function below implements this construction.  It does **not**
invoke any solver – it merely builds the graph.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def _add_edge(edges: set[Tuple[int, int]], u: int, v: int) -> None:
    """Add an undirected edge to ``edges``.

    The edge is stored with the smaller endpoint first to avoid duplicate
    entries like ``(u, v)`` and ``(v, u)``.
    """
    if u == v:
        # Self‑loops are never needed for the reduction and would make the
        # instance invalid, so we simply ignore them.
        return
    if u > v:
        u, v = v, u
    edges.add((u, v))


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three literals each).  Literals are represented as signed integers –
        exactly as described in the problem statement.

    Returns
    -------
    dict
        A graph instance for the ``ThreeColoring`` problem with keys ``"n"``
        and ``"edges"``.
    """
    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Vertex indices:
    # 0 -> T, 1 -> F, 2 -> B
    T, F, B = 0, 1, 2
    next_vertex = 3

    # Mapping from literal (signed int) to vertex index.
    lit_to_vertex: dict[int, int] = {}

    # Build edges set to avoid duplicates.
    edges: set[Tuple[int, int]] = set()

    # 1. Triangle of the three colour vertices.
    _add_edge(edges, T, F)
    _add_edge(edges, F, B)
    _add_edge(edges, T, B)

    # 2. Variable gadgets.
    for var in range(1, m + 1):
        pos = next_vertex
        neg = next_vertex + 1
        next_vertex += 2

        lit_to_vertex[+var] = pos
        lit_to_vertex[-var] = neg

        # Connect each literal vertex to B (cannot take base colour).
        _add_edge(edges, pos, B)
        _add_edge(edges, neg, B)
        # Edge between the two literals forces opposite colours.
        _add_edge(edges, pos, neg)

    # 3. Clause gadgets.
    for clause in clauses:
        if len(clause) != 3:
            # According to the specification each clause has exactly three
            # literals, but we guard against malformed input.
            raise ValueError("Each clause must contain exactly three literals")
        # Create three vertices for the clause triangle.
        c_vertices = [next_vertex, next_vertex + 1, next_vertex + 2]
        next_vertex += 3

        # Form the triangle among them.
        _add_edge(edges, c_vertices[0], c_vertices[1])
        _add_edge(edges, c_vertices[1], c_vertices[2])
        _add_edge(edges, c_vertices[0], c_vertices[2])

        # Connect each clause vertex to the corresponding literal vertex.
        for lit, cv in zip(clause, c_vertices):
            lit_vertex = lit_to_vertex.get(lit)
            if lit_vertex is None:
                # This can happen if a variable appears in a clause but the
                # formula declared fewer variables.  The original problem
                # definition guarantees consistency, so we raise an error to
                # surface the bug.
                raise ValueError(f"Literal {lit} refers to an undefined variable")
            _add_edge(edges, cv, lit_vertex)

    # Prepare final instance.
    edge_list = [[u, v] for (u, v) in edges]
    return {"n": next_vertex, "edges": edge_list}

