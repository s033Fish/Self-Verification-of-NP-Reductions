"""Reduction from NAE-3-SAT to 3-Coloring.

The source problem (NAE-3-SAT) is defined in ``problems.py`` as a
dictionary with keys ``num_vars`` and ``clauses``.  A clause is a list of
three literals.  A literal is an integer where a positive value ``+v``
means the variable *v* is true and a negative value ``-v`` means the
variable *v* is false.

The target problem (3-Coloring) expects a graph given by the number of
vertices ``n`` and a list of undirected edges ``edges`` where each edge
is a two‑element list ``[u, v]`` with ``u != v``.

The reduction follows the classic polynomial‑time construction used in
complexity textbooks:

* Introduce three special vertices that will be coloured *True*, *False*
  and *Base*.  They form a triangle, forcing any proper 3‑colouring to
  assign three distinct colours to them.
* For each variable ``x_i`` create two vertices ``p_i`` (positive literal)
  and ``n_i`` (negative literal).  Both are adjacent to the ``Base``
  vertex, so they cannot take the *Base* colour and must be coloured
  either *True* or *False*.  An edge between ``p_i`` and ``n_i`` forces
  them to receive opposite colours – exactly the relationship between a
  variable and its negation.
* For each clause ``(ℓ1, ℓ2, ℓ3)`` create three new vertices
  ``c1, c2, c3`` that form a triangle.  Vertex ``ck`` is connected to the
  vertex representing literal ``ℓk`` (either ``p_i`` or ``n_i``).  This
  gadget enforces the *Not‑All‑Equal* condition: if all three literals
  received the same truth colour, the three clause vertices would be
  forced to use only the two remaining colours, which is impossible for a
  triangle.  Conversely, if at least one literal is true and at least one
  is false, a proper 3‑colouring exists.

The construction runs in time linear in the size of the formula and
produces a graph that is 3‑colourable iff the original NAE‑3‑SAT instance
has a satisfying assignment.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``num_vars`` (int) and ``clauses`` (list of
        three‑element lists of literals).

    Returns
    -------
    dict
        A graph represented as ``{"n": n, "edges": [[u, v], ...]}``.
    """

    m = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    edges: List[List[int]] = []

    # ----- special triangle (True, False, Base) -----
    # Assign fixed indices for the three colour vertices.
    TRUE = 0
    FALSE = 1
    BASE = 2
    # Triangle among them
    edges.append([TRUE, FALSE])
    edges.append([TRUE, BASE])
    edges.append([FALSE, BASE])

    next_vertex = 3  # next free index after the three special vertices

    # ----- variable vertices -----
    # For each variable i (1‑based) we create two vertices: pos_i and neg_i.
    pos_vertices = [0] * (m + 1)  # index by variable number
    neg_vertices = [0] * (m + 1)
    for i in range(1, m + 1):
        pos = next_vertex
        neg = next_vertex + 1
        next_vertex += 2
        pos_vertices[i] = pos
        neg_vertices[i] = neg

        # Both are adjacent to BASE so they cannot take the BASE colour.
        edges.append([pos, BASE])
        edges.append([neg, BASE])
        # Edge between them forces opposite colours (True/False).
        edges.append([pos, neg])

    # ----- clause gadgets -----
    for clause in clauses:
        if len(clause) != 3:
            # According to the specification clauses always have length 3,
            # but we defensively ignore malformed ones.
            continue
        # Create three clause vertices forming a triangle.
        c_vertices = [next_vertex, next_vertex + 1, next_vertex + 2]
        next_vertex += 3
        # Triangle among clause vertices
        edges.append([c_vertices[0], c_vertices[1]])
        edges.append([c_vertices[1], c_vertices[2]])
        edges.append([c_vertices[2], c_vertices[0]])

        # Connect each clause vertex to the appropriate literal vertex.
        for lit, c_vert in zip(clause, c_vertices):
            var = abs(lit)
            if var == 0 or var > m:
                # Invalid variable index – skip (validation will catch it).
                continue
            if lit > 0:
                lit_vertex = pos_vertices[var]
            else:
                lit_vertex = neg_vertices[var]
            edges.append([c_vert, lit_vertex])

    # Ensure edges are stored with smaller index first for consistency.
    normalized_edges = [[u, v] if u < v else [v, u] for u, v in edges]

    # Remove potential duplicate edges (the construction does not create any,
    # but we guard against accidental duplicates).
    seen = set()
    unique_edges: List[List[int]] = []
    for u, v in normalized_edges:
        if (u, v) not in seen:
            seen.add((u, v))
            unique_edges.append([u, v])

    return {"n": next_vertex, "edges": unique_edges}

