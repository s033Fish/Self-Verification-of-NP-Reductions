"""Reduction from SAT to Independent Set.

The source problem is defined in ``problems.py`` as ``Sat`` with the
instance format ``{"num_vars": m, "clauses": [[literal, ...], ...]}``.
The target problem is ``IndependentSet`` with the instance format
``{"n": n, "edges": [[u, v], ...], "k": k}``.

We implement the classic polynomial‑time reduction: each literal in a
clause becomes a vertex. Vertices belonging to the same clause are made
pairwise adjacent (forming a clique). Additionally, vertices that are
complementary literals – i.e. they refer to the same variable with opposite
sign – are connected by an edge.  An independent set of size equal to the
number of clauses corresponds exactly to a satisfying assignment of the
formula.

Edge cases handled:
* Zero clauses – SAT is trivially satisfiable.  We output a graph with
  ``k = 0`` (any graph works, we choose ``n = 0`` and no edges) which is
  always a yes‑instance for Independent Set.
* An empty clause ``[]`` – the formula is unsatisfiable.  The reduction
  creates a graph where the clause contributes no vertices, but ``k`` is
  still the total number of clauses (>0).  No independent set can reach that
  size, so the target instance is a no‑instance, matching the source.

The implementation runs in time polynomial in the size of the SAT
instance and produces a valid Independent Set instance according to the
validation rules in ``problems.py``.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Set


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        A SAT instance as described in ``Sat``.

    Returns
    -------
    dict
        An Independent Set instance.  The answer to the returned instance
        is *yes* iff the original SAT instance is satisfiable.
    """

    # Extract data from the SAT instance.
    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case: no clauses – SAT is trivially satisfiable.
    if num_clauses == 0:
        # Any graph works; we use the empty graph.
        return {"n": 0, "edges": [], "k": 0}

    # Build vertices.  For each literal we store (var, sign) where sign is
    # +1 for a positive literal and -1 for a negative literal.
    # vertex_id runs from 0 to n-1.
    vertex_info: List[Tuple[int, int]] = []  # (var, sign)
    clause_vertices: List[List[int]] = []  # list of vertex ids per clause
    for clause in clauses:
        current_clause_vertices: List[int] = []
        for lit in clause:
            var = abs(lit)
            sign = 1 if lit > 0 else -1
            vertex_id = len(vertex_info)
            vertex_info.append((var, sign))
            current_clause_vertices.append(vertex_id)
        clause_vertices.append(current_clause_vertices)

    n = len(vertex_info)
    edges_set: Set[Tuple[int, int]] = set()

    # 1. Add edges inside each clause (clique).
    for verts in clause_vertices:
        for i in range(len(verts)):
            for j in range(i + 1, len(verts)):
                u, v = verts[i], verts[j]
                if u > v:
                    u, v = v, u
                edges_set.add((u, v))

    # 2. Add edges between complementary literals.
    #    We compare all pairs of vertices (could be optimized, but fine for
    #    polynomial size).
    for u in range(n):
        var_u, sign_u = vertex_info[u]
        for v in range(u + 1, n):
            var_v, sign_v = vertex_info[v]
            if var_u == var_v and sign_u != sign_v:
                edges_set.add((u, v))

    # Convert edge set to list of [u, v] with u < v as required.
    edges: List[List[int]] = [[u, v] for (u, v) in edges_set]

    return {"n": n, "edges": edges, "k": num_clauses}

