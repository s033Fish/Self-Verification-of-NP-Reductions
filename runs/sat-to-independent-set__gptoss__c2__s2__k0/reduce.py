"""Reduction from SAT to Independent Set.

The source problem is defined in ``problems.py`` as ``Sat`` with the
instance format ``{"num_vars": m, "clauses": [[literal, ...], ...]}``.
The target problem is ``IndependentSet`` with format
``{"n": n, "edges": [[u, v], ...], "k": k}``.

We implement the classic polynomial‑time reduction:

* For each clause create a *clique* (complete subgraph) containing one
  vertex for every literal occurrence in that clause.
* Connect vertices belonging to different clauses when the represented
  literals are contradictory (e.g. ``+x`` and ``-x``).  These edges
  prevent an independent set from selecting both a variable and its
  negation.
* Set ``k`` to the number of clauses.  An independent set of size ``k``
  corresponds to picking exactly one literal from each clause such that
  no two chosen literals contradict each other – precisely a satisfying
  assignment.

The reduction respects the edge cases described in the problem
specifications:

* If the formula has **no clauses**, it is trivially satisfiable.  We
  output an empty graph with ``k = 0`` – which is always a yes instance
  of Independent Set.
* If a clause is empty, the reduction creates no vertex for that clause.
  Since ``k`` equals the total number of clauses, an independent set of
  size ``k`` cannot exist, matching the unsatisfiable nature of a formula
  containing an empty clause.

The implementation runs in O(V²) time where V is the total number of
literal occurrences, which is polynomial in the size of the SAT
instance.
"""

from __future__ import annotations

from typing import List, Tuple, Set


def reduce(instance: dict) -> dict:
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        A SAT instance following the format described above.

    Returns
    -------
    dict
        An Independent Set instance.  The answer to this instance is
        "yes" iff the original SAT instance is satisfiable.
    """

    # Extract clauses; we do not need ``num_vars`` for the construction.
    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Edge case: no clauses → trivially satisfiable.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Assign a vertex id to each literal occurrence.
    # Store (clause_index, literal) for later edge construction.
    vertex_info: List[Tuple[int, int]] = []  # (clause_idx, literal)
    clause_vertices: List[List[int]] = []  # list of vertex ids per clause
    for ci, clause in enumerate(clauses):
        current_clause_vertices: List[int] = []
        for lit in clause:
            vid = len(vertex_info)
            vertex_info.append((ci, lit))
            current_clause_vertices.append(vid)
        clause_vertices.append(current_clause_vertices)

    n = len(vertex_info)
    edge_set: Set[Tuple[int, int]] = set()

    # 1. Add clique edges inside each clause.
    for verts in clause_vertices:
        l = len(verts)
        for i in range(l):
            for j in range(i + 1, l):
                u, v = verts[i], verts[j]
                if u > v:
                    u, v = v, u
                edge_set.add((u, v))

    # 2. Add conflict edges between contradictory literals of different clauses.
    #    For each pair of vertices from distinct clauses, if lit1 == -lit2, connect.
    for u in range(n):
        ci_u, lit_u = vertex_info[u]
        for v in range(u + 1, n):
            ci_v, lit_v = vertex_info[v]
            if ci_u == ci_v:
                continue  # already handled by clique edges
            if lit_u == -lit_v:
                edge_set.add((u, v))

    # Convert edge set to required list format.
    edges = [[u, v] for (u, v) in sorted(edge_set)]

    return {"n": n, "edges": edges, "k": num_clauses}

