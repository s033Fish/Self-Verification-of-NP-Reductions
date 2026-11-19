"""Reduction from 3‑SAT to 3‑Coloring.

The source problem is :class:`ThreeSat` (defined in ``problems.py``) and the
target problem is :class:`ThreeColoring`.  Both classes only provide a
``validate`` method – they do **not** contain solvers.  The reduction must be
polynomial time and must preserve the answer (yes‑instance ↔ yes‑instance).

The construction follows the classic textbook reduction (see Garey &
Johnson, *Computers and Intractability*).  We use three distinguished vertices
forming a triangle – they will be forced to receive three different colours
which we interpret as the logical constants **TRUE**, **FALSE** and a neutral
**BASE** colour.

Variable gadget
----------------
For each variable ``x_i`` we create two vertices ``pos_i`` and ``neg_i``.
Both are adjacent to the BASE vertex, so they cannot be coloured BASE and are
restricted to the TRUE/FALSE colours.  An edge between ``pos_i`` and ``neg_i``
forces them to receive different colours, i.e. exactly one of them is TRUE and
the other FALSE.  ``pos_i`` represents the literal ``x_i`` and ``neg_i`` the
literal ``¬x_i``.

Clause gadget
-------------
For each clause ``(ℓ1 ∨ ℓ2 ∨ ℓ3)`` we create three new vertices forming a
triangle.  Each of the three vertices is connected to the vertex that
represents the corresponding literal (``pos_i`` or ``neg_i``).  If all three
literals are coloured FALSE, then each clause‑vertex is forbidden from using
the FALSE colour and the triangle would have to be coloured with only two
colours – impossible.  Hence a proper 3‑colouring exists iff every clause has
at least one true literal.

The reduction runs in time linear in the size of the formula and therefore
is polynomial.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeSat, ThreeColoring

def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.  The
        instance is assumed to be valid – ``ThreeSat.validate`` is called to
        guard against malformed input.

    Returns
    -------
    dict
        A graph ``{"n": n, "edges": [[u, v], ...]}`` suitable for the
        ``ThreeColoring`` problem.
    """

    # Validate the source instance – this will raise InvalidInstance if the
    # format is wrong.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    edges: List[List[int]] = []

    # Vertex numbering:
    # 0 = TRUE, 1 = FALSE, 2 = BASE (the triangle of constants)
    TRUE, FALSE, BASE = 0, 1, 2
    # Add the base triangle.
    edges.append([TRUE, FALSE])
    edges.append([TRUE, BASE])
    edges.append([FALSE, BASE])

    # Mapping from variable index to the two literal vertices.
    pos: List[int] = []  # pos[i] is vertex for literal + (i+1)
    neg: List[int] = []  # neg[i] is vertex for literal - (i+1)

    next_id = 3  # next free vertex identifier
    for _ in range(m):
        p = next_id
        n = next_id + 1
        next_id += 2
        pos.append(p)
        neg.append(n)
        # Both literal vertices are adjacent to BASE so they cannot take the
        # BASE colour.
        edges.append([p, BASE])
        edges.append([n, BASE])
        # They are adjacent to each other, forcing opposite colours (TRUE/FALSE).
        edges.append([p, n])

    # Clause gadgets.
    for clause in clauses:
        # Create three vertices for the clause triangle.
        c_vertices = [next_id, next_id + 1, next_id + 2]
        next_id += 3
        # Triangle edges among the three clause vertices.
        edges.append([c_vertices[0], c_vertices[1]])
        edges.append([c_vertices[1], c_vertices[2]])
        edges.append([c_vertices[2], c_vertices[0]])
        # Connect each clause vertex to the appropriate literal vertex.
        for lit, cv in zip(clause, c_vertices):
            var = abs(lit) - 1  # zero‑based variable index
            if lit > 0:
                lit_vertex = pos[var]
            else:
                lit_vertex = neg[var]
            edges.append([cv, lit_vertex])

    # Build the final instance.
    graph_instance: Dict[str, Any] = {"n": next_id, "edges": edges}
    # Validate the constructed target instance (helps catch bugs).
    ThreeColoring.validate(graph_instance)
    return graph_instance

