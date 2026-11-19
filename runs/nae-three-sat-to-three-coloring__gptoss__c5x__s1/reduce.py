"""Reduction from NAE‑3‑SAT to 3-Coloring.

This implements the classic polynomial‑time reduction from NAE‑3‑SAT to
3‑Coloring (see Garey & Johnson).  The reduction builds a graph that can be
3‑coloured iff the original NAE‑3‑SAT formula has a not‑all‑equal satisfying
assignment.

Construction outline
---------------------
* Create three base vertices (0,1,2) forming a triangle.  These represent the
  three colours.  Vertex 2 (called ``B``) will be the colour that literals are
  forced *not* to take.
* For each variable *x* create two vertices ``p_x`` and ``n_x`` (positive and
  negative literal).  Connect them with an edge and also connect each of them
  to the base vertex ``B``.  In any proper 3‑colouring ``p_x`` and ``n_x`` must
  receive opposite colours among the remaining two colours (the colours of
  vertices 0 and 1).  Thus a truth assignment can be read off: colour 0 → true,
  colour 1 → false.
* For each clause (ℓ₁,ℓ₂,ℓ₃) add a triangle of three new vertices.  Connect each
  vertex of this triangle to the vertex representing the corresponding literal
  (positive or negative) of the clause.  The clause triangle can be properly
  coloured iff the three incident literal vertices are not all the same colour,
  which is exactly the NAE condition.

The reduction runs in time O(m + |clauses|) and produces a graph in the format
expected by the ``ThreeColoring`` problem definition.
"""

from __future__ import annotations

from typing import Dict, List, Any

from problems import NaeThreeSat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance: dict
        A valid NAE‑3‑SAT instance as described in ``problems.NaeThreeSat``.

    Returns
    -------
    dict
        A graph instance suitable for ``ThreeColoring``.
    """
    # Validate the input instance.
    NaeThreeSat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    edges: List[List[int]] = []

    def add_edge(u: int, v: int) -> None:
        if u == v:
            raise ValueError("self-loop not allowed")
        # store in canonical order to ease duplicate removal later
        if u > v:
            u, v = v, u
        edges.append([u, v])

    # Base triangle vertices: 0 = T, 1 = F, 2 = B (the colour that literals avoid)
    T, F, B = 0, 1, 2
    add_edge(T, F)
    add_edge(F, B)
    add_edge(B, T)

    next_vid = 3  # next free vertex identifier
    pos: Dict[int, int] = {}
    neg: Dict[int, int] = {}
    for var in range(1, num_vars + 1):
        p_id = next_vid
        n_id = next_vid + 1
        next_vid += 2
        pos[var] = p_id
        neg[var] = n_id
        # Force opposite colours and forbid colour B
        add_edge(p_id, n_id)
        add_edge(p_id, B)
        add_edge(n_id, B)

    # Clause gadgets
    for clause in clauses:
        # Create three new vertices forming a triangle
        c1, c2, c3 = next_vid, next_vid + 1, next_vid + 2
        next_vid += 3
        add_edge(c1, c2)
        add_edge(c2, c3)
        add_edge(c3, c1)
        # Connect each clause vertex to the appropriate literal vertex
        for lit, c_vid in zip(clause, (c1, c2, c3)):
            var = abs(lit)
            lit_vid = pos[var] if lit > 0 else neg[var]
            add_edge(c_vid, lit_vid)

    # Remove duplicate edges (if any) while preserving list format
    unique = {frozenset((e[0], e[1])): e for e in edges}
    final_edges = list(unique.values())

    return {"n": next_vid, "edges": final_edges}

