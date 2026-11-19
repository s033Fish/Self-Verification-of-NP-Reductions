"""Reduction from 3‑SAT to 3‑Coloring.

The source problem (``ThreeSat``) is described in ``problems.py``.  An
instance is a dictionary with keys ``"num_vars"`` (the number of variables
``m``) and ``"clauses"`` (a list of clauses, each a list of three literals).
Literals are encoded as signed integers: ``+v`` means the variable ``v`` is
true, ``-v`` means it is false.

The target problem (``ThreeColoring``) expects a graph given by the number
of vertices ``n`` and a list of undirected edges ``edges`` where each edge is
``[u, v]`` with ``0 <= u < v < n`` and no duplicate edges.

The classic polynomial‑time reduction works as follows (see any textbook on
NP‑completeness):

* Introduce three special vertices that will receive the three colours.  We
  call them ``TRUE``, ``FALSE`` and ``BASE``.  They form a triangle so that
  they must be coloured with three distinct colours.
* For each variable ``x_i`` create two vertices ``x_i`` and ``¬x_i``.  Both
  are adjacent to ``BASE`` (so they cannot take the colour of ``BASE``) and
  they are adjacent to each other, forcing them to receive the colours of
  ``TRUE`` and ``FALSE`` – one true, one false.
* For each clause ``(ℓ₁ ∨ ℓ₂ ∨ ℓ₃)`` create three new vertices forming a
  triangle.  Vertex ``c_j`` of the triangle is connected to the vertex that
  represents the literal ℓ_j.  The clause triangle is *not* connected to
  ``BASE``.  Because the triangle must use all three colours, at least one of
  its vertices must obtain the colour of ``BASE``.  That can happen only if
  the corresponding literal vertex is **not** coloured with the same colour
  (it is adjacent), which forces that literal to be coloured ``TRUE``.  If
  all three literals are coloured ``FALSE`` the clause triangle would have
  only two admissible colours (``TRUE`` and ``BASE``) and could not be
  properly coloured – the graph would be not 3‑colourable.

Consequently the constructed graph is 3‑colourable iff the original 3‑SAT
formula is satisfiable.

The implementation below follows exactly this construction.  It runs in
time linear in the size of the SAT instance and produces a valid graph
according to the ``ThreeColoring`` specification.
"""

from __future__ import annotations

from typing import Dict, List


def _add_edge(edges: List[List[int]], u: int, v: int) -> None:
    """Append an undirected edge ``[u, v]`` with ``u < v`` to ``edges``.

    The reduction never creates duplicate edges, but we keep the helper to
    guarantee the ordering required by the ``validate`` function in
    ``problems.py``.
    """
    if u == v:
        raise ValueError("self‑loops are not allowed in the reduction")
    if u > v:
        u, v = v, u
    edges.append([u, v])


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``

    Returns
    -------
    dict
        ``{"n": n, "edges": [[u, v], ...]}`` representing the constructed
        graph.
    """
    # ------------------------------------------------------------------
    # Extract the SAT data.
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # ------------------------------------------------------------------
    # Vertex layout (indices start at 0):
    #   0,1,2               – the special triangle (TRUE, FALSE, BASE)
    #   3 .. 3+2*m-1       – variable vertices: for each i (1‑based)
    #                         true_i = 3 + 2*(i-1)
    #                         false_i = true_i + 1
    #   after that          – clause gadgets, three vertices per clause.
    # ------------------------------------------------------------------
    TRUE = 0
    FALSE = 1
    BASE = 2

    edges: List[List[int]] = []

    # Special triangle.
    _add_edge(edges, TRUE, FALSE)
    _add_edge(edges, FALSE, BASE)
    _add_edge(edges, TRUE, BASE)

    # Variable vertices.
    var_true_idx = []  # index of the vertex representing the literal +i
    var_false_idx = []  # index of the vertex representing the literal -i
    for i in range(1, m + 1):
        true_idx = 3 + 2 * (i - 1)
        false_idx = true_idx + 1
        var_true_idx.append(true_idx)
        var_false_idx.append(false_idx)
        # Connect each literal vertex to BASE so they cannot take the BASE colour.
        _add_edge(edges, true_idx, BASE)
        _add_edge(edges, false_idx, BASE)
        # Edge between the two literals forces opposite colours (TRUE/FALSE).
        _add_edge(edges, true_idx, false_idx)

    # Clause gadgets.
    clause_start = 3 + 2 * m
    for ci, clause in enumerate(clauses):
        # Expect exactly three literals.
        if len(clause) != 3:
            raise ValueError("Each clause must contain exactly three literals")
        # Create three vertices for the clause triangle.
        c0 = clause_start + ci * 3
        c1 = c0 + 1
        c2 = c0 + 2
        # Triangle edges.
        _add_edge(edges, c0, c1)
        _add_edge(edges, c1, c2)
        _add_edge(edges, c0, c2)
        # Connect each clause vertex to the vertex representing its literal.
        clause_vertices = [c0, c1, c2]
        for lit, cv in zip(clause, clause_vertices):
            var = abs(lit)
            if var == 0 or var > m:
                raise ValueError("Literal refers to non‑existent variable")
            if lit > 0:
                lit_vertex = var_true_idx[var - 1]
            else:
                lit_vertex = var_false_idx[var - 1]
            _add_edge(edges, cv, lit_vertex)

    n_vertices = clause_start + 3 * len(clauses)
    return {"n": n_vertices, "edges": edges}

