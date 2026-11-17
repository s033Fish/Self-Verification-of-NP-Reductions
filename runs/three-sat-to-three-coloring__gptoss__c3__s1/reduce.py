"""Reduction from 3‑SAT to 3‑Coloring.

The source problem is :class:`problems.ThreeSat` and the target is
``ThreeColoring``. Both classes are defined in *problems.py* and provide the
static methods ``validate`` and ``is_yes`` that we can use for testing.

The construction follows the classic textbook reduction:

* Create three special vertices forming a triangle.  They will be forced to
  take three distinct colours; we interpret them as the colours ``TRUE``,
  ``FALSE`` and ``BASE``.
* For each variable ``x_i`` we create two vertices ``pos_i`` and ``neg_i``.
  Both are adjacent to the ``BASE`` vertex, which forces them to use only the
  ``TRUE``/``FALSE`` colours.  An edge between ``pos_i`` and ``neg_i`` forces
  them to receive opposite colours, thereby encoding a truth assignment for the
  variable.
* For each clause ``(ℓ1 ∨ ℓ2 ∨ ℓ3)`` we create a triangle of three new
  vertices.  Vertex ``c_j`` of the clause triangle is connected to the literal
  vertex that represents ``ℓj`` (positive or negative).  The clause triangle
  can be properly 3‑coloured iff at least one of its three neighbouring literal
  vertices is coloured ``TRUE`` – exactly the condition that the clause is
  satisfied.

The resulting graph is 3‑colourable iff the original formula is satisfiable.
The construction runs in time linear in the size of the SAT instance, i.e. in
polynomial time.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes only for type‑checking / documentation.  The
# reduction itself must not call any solver methods.
import problems  # noqa: F401  (imported for side‑effects of class definitions)


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        in the docstring of :class:`problems.ThreeSat`.

    Returns
    -------
    dict
        A graph instance suitable for :class:`problems.ThreeColoring` – i.e.
        ``{"n": n, "edges": [[u, v], ...]}``.
    """

    # Extract data
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    edges: List[List[int]] = []

    # Helper to add an undirected edge (avoid duplicates by construction).
    def add_edge(u: int, v: int) -> None:
        if u == v:
            raise ValueError("self‑loop not allowed in reduction")
        edges.append([u, v])

    # ------------------------------------------------------------------
    # 1. Special vertices: TRUE = 0, FALSE = 1, BASE = 2 (forming a triangle).
    TRUE, FALSE, BASE = 0, 1, 2
    add_edge(TRUE, FALSE)
    add_edge(FALSE, BASE)
    add_edge(BASE, TRUE)

    next_vertex = 3  # next free index

    # ------------------------------------------------------------------
    # 2. Variable gadgets.
    # Store the vertex indices for the literal vertices so that clause gadgets
    # can refer to them.
    pos_lit: List[int] = [0] * (m + 1)  # 1‑based indexing, unused entry 0
    neg_lit: List[int] = [0] * (m + 1)

    for var in range(1, m + 1):
        pos = next_vertex
        neg = next_vertex + 1
        next_vertex += 2
        pos_lit[var] = pos
        neg_lit[var] = neg

        # Both literals are adjacent to BASE so they cannot take the BASE colour.
        add_edge(pos, BASE)
        add_edge(neg, BASE)
        # Edge between the two literals forces opposite colours (TRUE/FALSE).
        add_edge(pos, neg)

    # ------------------------------------------------------------------
    # 3. Clause gadgets.
    for clause in clauses:
        # clause is a list of three literals, each non‑zero integer.
        # Create three new vertices for this clause.
        c_vertices = [next_vertex, next_vertex + 1, next_vertex + 2]
        next_vertex += 3
        # Form a triangle among them.
        add_edge(c_vertices[0], c_vertices[1])
        add_edge(c_vertices[1], c_vertices[2])
        add_edge(c_vertices[2], c_vertices[0])

        # Connect each clause vertex to the appropriate literal vertex.
        for lit, c_vert in zip(clause, c_vertices):
            var = abs(lit)
            if var > m:
                # This should not happen in a valid instance, but we keep the
                # code robust.
                raise ValueError("literal refers to non‑existent variable")
            lit_vertex = pos_lit[var] if lit > 0 else neg_lit[var]
            add_edge(c_vert, lit_vertex)

    # ------------------------------------------------------------------
    # Assemble the final graph instance.
    n = next_vertex  # total number of vertices used
    return {"n": n, "edges": edges}

