"""Reduction from NAE-3-SAT to 3-Coloring.

The source problem is :class:`problems.NaeThreeSat` and the target is
``problems.ThreeColoring``.  Both classes are defined in *problems.py* and
provide ``validate`` and ``is_yes`` methods.  The reduction follows the
standard textbook construction:

* Introduce a distinguished *base* vertex ``b``.  In any proper 3‑coloring
  ``b`` will receive one colour (call it colour 0).
* For each variable ``x`` create two vertices ``x_pos`` and ``x_neg``.  Both
  are adjacent to ``b`` (forcing them to avoid colour 0) and are adjacent to
  each other (forcing them to receive the two remaining colours, which we
  interpret as *TRUE* and *FALSE* respectively).
* For each clause ``(ℓ₁, ℓ₂, ℓ₃)`` create three new vertices forming a
  triangle.  The ``j``‑th vertex of the triangle is connected to the vertex
  representing literal ``ℓⱼ``.  The triangle forces its three vertices to be
  all three different colours.  Because each is adjacent to its literal, it
  cannot take the colour assigned to that literal.  Consequently the clause
  gadget is colourable iff the three literals are **not** all equal – exactly
  the NAE condition.

The construction runs in polynomial time and produces a simple undirected
graph suitable for the ``ThreeColoring`` format.
"""

from __future__ import annotations

from typing import Dict, List

# Import the problem classes only for validation (optional).  Importing the
# module also makes the classes available for type‑checking tools.
import problems


def reduce(instance: Dict) -> Dict:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``NaeThreeSat`` specification:
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}`` where each literal
        is an integer ``+v`` (positive) or ``-v`` (negative).

    Returns
    -------
    dict
        A graph instance for ``ThreeColoring``:
        ``{"n": n, "edges": [[u, v], ...]}``.
    """

    # Validate the source instance – this will raise if the format is wrong.
    problems.NaeThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    edges: List[List[int]] = []
    next_id = 0

    # 0 – the base vertex.
    base = next_id
    next_id += 1

    # Maps from variable index to the vertex ids of its positive and negative
    # literal vertices.
    pos_id: List[int] = [0] * (m + 1)  # 1‑based indexing, ignore index 0
    neg_id: List[int] = [0] * (m + 1)

    for var in range(1, m + 1):
        p = next_id
        next_id += 1
        n = next_id
        next_id += 1
        pos_id[var] = p
        neg_id[var] = n

        # Connect both literals to the base vertex.
        edges.append([base, p])
        edges.append([base, n])
        # Positive and negative literals must get opposite colours.
        edges.append([p, n])

    # Clause gadgets.
    for clause in clauses:
        # clause is a list of three literals.
        assert len(clause) == 3
        # Create three vertices for the clause triangle.
        c_vertices = []
        for _ in range(3):
            c = next_id
            next_id += 1
            c_vertices.append(c)
        # Add the triangle edges.
        edges.append([c_vertices[0], c_vertices[1]])
        edges.append([c_vertices[1], c_vertices[2]])
        edges.append([c_vertices[2], c_vertices[0]])

        # Connect each clause vertex to the appropriate literal vertex.
        for lit, cv in zip(clause, c_vertices):
            var = abs(lit)
            if lit > 0:
                lit_vertex = pos_id[var]
            else:
                lit_vertex = neg_id[var]
            edges.append([lit_vertex, cv])

    # Assemble the final graph instance.
    graph_instance = {"n": next_id, "edges": edges}
    # Validate the target instance to catch programming mistakes early.
    problems.ThreeColoring.validate(graph_instance)
    return graph_instance

