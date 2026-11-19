"""Reduction from SAT to Independent Set.

The source problem is SAT in conjunctive normal form.  An instance is a
dictionary with the keys ``num_vars`` (the number of variables) and
``clauses`` (a list of clauses).  Each clause is itself a list of literals
where a literal is a string ``"+v"`` meaning variable *v* is true or
``"-v"`` meaning variable *v* is false.  The format is described in the
project's ``problems.py`` file.

The target problem is Independent Set.  An instance is a dictionary with the
keys ``n`` (number of vertices), ``edges`` (list of undirected edges) and
``k`` (the required size of the independent set).  Vertices are numbered
``0 .. n-1``.

The classic polynomial‑time reduction works as follows:

* For each clause create a vertex for **each** literal occurring in that
  clause.  Vertices belonging to the same clause form a clique – we add an
  edge between every pair of vertices of the same clause.  This forces an
  independent set to contain at most one vertex from each clause.
* For any two vertices belonging to different clauses, add an edge when the
  corresponding literals are complementary (``+v`` vs ``-v``).  This
  prevents the independent set from selecting contradictory assignments.
* Set ``k`` to the number of clauses.  An independent set of size ``k``
  exists iff the SAT formula is satisfiable.

The reduction handles the edge cases required by the specification:

* If the formula has **no clauses**, it is trivially satisfiable.  The
  reduction returns a graph with ``n = 0`` vertices, an empty edge list and
  ``k = 0`` – the Independent Set instance is a yes‑instance because ``k <=
  0``.
* If a clause is empty, the formula is unsatisfiable.  The clause contributes
  no vertices, so the maximum possible independent set size is strictly less
  than the total number of clauses, making the Independent Set instance a
  no‑instance.

The implementation runs in polynomial time with respect to the size of the
input (``O(V^2)`` edges in the worst case, which is acceptable for a reduction
script).
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def _parse_literal(lit: str) -> Tuple[int, int]:
    """Return ``(var, sign)`` where ``sign`` is ``+1`` for ``+v`` and ``-1`` for ``-v``.

    The function assumes the literal format is exactly as specified in the
    problem statement.
    """
    if not lit:
        raise ValueError("Empty literal string")
    sign = 1 if lit[0] == "+" else -1
    var = int(lit[1:])
    return var, sign


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        A SAT instance with keys ``num_vars`` and ``clauses`` as described
        above.

    Returns
    -------
    dict
        An Independent Set instance ``{"n": n, "edges": edges, "k": k}``.
    """
    clauses: List[List[str]] = instance.get("clauses", [])
    k = len(clauses)

    # Edge case: no clauses → trivially satisfiable.
    if k == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Build vertices.  We keep a list of (clause_index, literal_string).
    vertices: List[Tuple[int, str]] = []
    clause_vertices: List[List[int]] = []  # indices of vertices belonging to each clause
    for ci, clause in enumerate(clauses):
        current_indices: List[int] = []
        for lit in clause:
            idx = len(vertices)
            vertices.append((ci, lit))
            current_indices.append(idx)
        clause_vertices.append(current_indices)

    n = len(vertices)
    edges: List[List[int]] = []

    # 1. Add edges inside each clause to make a clique.
    for idxs in clause_vertices:
        l = len(idxs)
        for i in range(l):
            for j in range(i + 1, l):
                edges.append([idxs[i], idxs[j]])

    # 2. Add edges between complementary literals from different clauses.
    # Pre‑compute literal info for each vertex.
    lit_info: List[Tuple[int, int]] = []  # (var, sign)
    for _, lit in vertices:
        var, sign = _parse_literal(lit)
        lit_info.append((var, sign))

    for i in range(n):
        ci, _ = vertices[i]
        vi, si = lit_info[i]
        for j in range(i + 1, n):
            cj, _ = vertices[j]
            if ci == cj:
                # already handled by clause clique
                continue
            vj, sj = lit_info[j]
            if vi == vj and si != sj:
                edges.append([i, j])

    return {"n": n, "edges": edges, "k": k}

