"""Reduction from NAE-3-SAT to 3-Coloring.

The reduction follows the classic construction:

* Introduce three special vertices forming a triangle. Their colours are
  interpreted as **TRUE**, **FALSE**, and **BASE**.
* For each variable ``x`` create two vertices ``pos_x`` and ``neg_x``
  (representing the literal ``x`` and ``¬x``). Both are adjacent to the
  BASE vertex, therefore each must be coloured either TRUE or FALSE.
  An additional edge between ``pos_x`` and ``neg_x`` forces them to take
  opposite colours, establishing a consistent truth assignment.
* For each clause ``(ℓ1, ℓ2, ℓ3)`` create a triangle of three fresh
  vertices ``c1, c2, c3``. Vertex ``ci`` is connected to the vertex that
  represents literal ``ℓi`` (either ``pos_x`` or ``neg_x``). The clause
  triangle can be properly 3‑coloured **iff** the three incident literals
  are not all coloured the same, which is exactly the NAE condition.

The construction is polynomial: ``O(m + |C|)`` vertices and edges.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def reduce(instance: Dict) -> Dict:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance: dict
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``
        Literals are integers ``+v`` for ``v`` true and ``-v`` for ``v`` false.

    Returns
    -------
    dict
        ``{"n": n, "edges": [[u, v], ...]}`` suitable for ``ThreeColoring``.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Vertex indexing strategy
    # 0,1,2 -> the base triangle (TRUE, FALSE, BASE)
    TRUE, FALSE, BASE = 0, 1, 2
    next_id = 3

    # For each variable x (1‑based), store ids of pos_x and neg_x
    pos: List[int] = [0] * (m + 1)  # ignore index 0
    neg: List[int] = [0] * (m + 1)
    for var in range(1, m + 1):
        pos[var] = next_id
        next_id += 1
        neg[var] = next_id
        next_id += 1

    # For each clause we will add three vertices forming a triangle
    clause_vertices: List[Tuple[int, int, int]] = []
    for _ in clauses:
        a = next_id
        b = next_id + 1
        c = next_id + 2
        clause_vertices.append((a, b, c))
        next_id += 3

    n = next_id  # total number of vertices
    edges: List[List[int]] = []

    # Helper to add an undirected edge (avoid duplicates by construction)
    def add(u: int, v: int) -> None:
        edges.append([u, v])

    # Base triangle
    add(TRUE, FALSE)
    add(FALSE, BASE)
    add(BASE, TRUE)

    # Variable vertices: each adjacent to BASE and opposite to each other
    for var in range(1, m + 1):
        add(pos[var], BASE)
        add(neg[var], BASE)
        add(pos[var], neg[var])

    # Clause gadgets
    for (clause, (a, b, c)) in zip(clauses, clause_vertices):
        # triangle among a,b,c
        add(a, b)
        add(b, c)
        add(c, a)
        # connect each clause vertex to the corresponding literal vertex
        literals = clause
        for lit, clause_vertex in zip(literals, (a, b, c)):
            var = abs(lit)
            if lit > 0:
                literal_vertex = pos[var]
            else:
                literal_vertex = neg[var]
            add(clause_vertex, literal_vertex)

    return {"n": n, "edges": edges}
