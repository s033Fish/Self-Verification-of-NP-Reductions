"""Reduction from 3‑SAT to Vertex Cover.

The source problem is represented by the ``ThreeSat`` class (see
``problems.py``).  An instance is a dictionary with the keys

* ``"num_vars"`` – the number *m* of Boolean variables (variables are
  numbered 1 … m),
* ``"clauses"`` – a list of clauses, each clause being a list of three
  integers.  A positive integer ``+v`` denotes the literal *x_v* and a
  negative integer ``-v`` denotes ``¬x_v``.

The target problem is ``VertexCover``.  An instance is a dictionary with
the keys

* ``"n"`` – number of vertices (labelled 0 … n‑1),
* ``"edges"`` – list of undirected edges ``[u, v]`` (no duplicate or
  self‑loops),
* ``"k"`` – the size bound for the vertex cover.

We implement the classic polynomial‑time reduction described in many
textbooks (e.g., Garey & Johnson).  For each Boolean variable *x_i* we
create two vertices ``pos_i`` and ``neg_i`` connected by an edge.  For
each clause we create a triangle of three vertices, one for each
literal, and connect each of those vertices to the corresponding
variable‑literal vertex.  The constructed graph has a vertex cover of
size ``m + 2·|C|`` (where ``|C|`` is the number of clauses) iff the
original formula is satisfiable.

The reduction runs in time linear in the size of the 3‑SAT instance,
which is polynomial.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Vertex‑Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as
        described above.

    Returns
    -------
    dict
        A vertex‑cover instance ``{"n": n, "edges": edges, "k": k}``.
    """

    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # ---------- Vertex set construction ----------
    # For each variable i (1‑based) we allocate two vertices:
    #   pos_i  -> index 2*(i-1)
    #   neg_i  -> index 2*(i-1) + 1
    # Total variable vertices: 2*m
    var_vertices = 2 * m

    # For each clause we allocate three vertices forming a triangle.
    # Clause j (0‑based) gets vertices starting at:
    #   clause_base + 3*j, where clause_base = var_vertices
    clause_base = var_vertices
    num_clauses = len(clauses)
    total_vertices = var_vertices + 3 * num_clauses

    edges: List[List[int]] = []

    # 1. Variable edges (pos_i -- neg_i)
    for i in range(m):
        edges.append([2 * i, 2 * i + 1])

    # 2. Clause gadgets: triangles and connections to variable literals
    for j, clause in enumerate(clauses):
        # Indices of the three clause vertices
        base = clause_base + 3 * j
        v0, v1, v2 = base, base + 1, base + 2

        # Triangle edges
        edges.append([v0, v1])
        edges.append([v1, v2])
        edges.append([v2, v0])

        # Connect each clause literal vertex to the appropriate variable literal vertex
        for t, lit in enumerate(clause):
            var = abs(lit) - 1  # zero‑based variable index
            if lit > 0:
                var_vertex = 2 * var       # positive literal vertex
            else:
                var_vertex = 2 * var + 1   # negative literal vertex
            clause_vertex = base + t
            edges.append([clause_vertex, var_vertex])

    # The size bound k = m + 2 * |C|
    k = m + 2 * num_clauses

    return {"n": total_vertices, "edges": edges, "k": k}

