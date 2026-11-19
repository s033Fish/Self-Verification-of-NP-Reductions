"""Reduction from SAT to Independent Set.

The source problem is SAT (CNF satisfiability) as defined in ``problems.py``.
The target problem is Independent Set.

Standard reduction:
    * For each clause create a *clique* of vertices – one vertex for each
      literal in the clause.
    * Add edges between vertices of *different* clauses when the literals are
      complementary (e.g. ``x`` and ``-x``). Selecting at most one vertex from
      each clause and never selecting complementary literals yields a
      satisfying assignment.
    * Set ``k`` (the required independent‑set size) to the number of clauses.

Correctness sketch:
    * If the formula is satisfiable, pick for each clause a literal that is
      true under a satisfying assignment. The corresponding vertices form an
      independent set of size exactly the number of clauses (no two are in the
      same clause, and complementary literals cannot both be true).
    * Conversely, an independent set of size equal to the number of clauses
      must contain exactly one vertex from each clause (cliques prevent more
      than one). The chosen literals cannot be complementary, so they define a
      consistent truth assignment that satisfies every clause.

Edge‑case handling mirrors the specification in ``problems.py``:
    * ``c == 0`` (no clauses) → ``k = 0`` and an empty graph – independent set
      of size ``0`` always exists.
    * A clause may be empty. In that case the reduction produces no vertex for
      that clause, so the total number of vertices is ``< c`` and the required
      independent‑set size ``k = c`` cannot be achieved, correctly reflecting
      unsatisfiability.

The function ``reduce`` validates the input using ``Sat.validate`` and returns
an instance suitable for ``IndependentSet.validate``.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import Sat, IndependentSet


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary representing a SAT instance as described in
        ``problems.Sat``.

    Returns
    -------
    dict
        An Independent Set instance ``{"n": n, "edges": [...], "k": k}``.
    """
    # Validate source instance – raises InvalidInstance on malformed input.
    Sat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    c = len(clauses)  # number of clauses, also target k

    # For each clause keep list of (literal, vertex_id). Duplicate literals get
    # distinct vertices, which is fine for the reduction.
    clause_vertices: List[List[Tuple[int, int]]] = []
    next_id = 0
    for clause in clauses:
        cur: List[Tuple[int, int]] = []
        for lit in clause:
            vid = next_id
            cur.append((lit, vid))
            next_id += 1
        clause_vertices.append(cur)

    n = next_id  # total number of vertices
    edges: List[List[int]] = []

    # 1. Make each clause a clique.
    for cur in clause_vertices:
        ids = [vid for _, vid in cur]
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                edges.append([ids[i], ids[j]])

    # 2. Add edges between complementary literals from different clauses.
    for ci1 in range(c):
        for ci2 in range(ci1 + 1, c):
            for lit1, v1 in clause_vertices[ci1]:
                for lit2, v2 in clause_vertices[ci2]:
                    if lit1 == -lit2:
                        edges.append([v1, v2])

    # Normalize edges (u < v) and deduplicate.
    normalized_edges: List[List[int]] = []
    seen = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        key = (u, v)
        if key not in seen:
            seen.add(key)
            normalized_edges.append([u, v])

    target_instance = {"n": n, "edges": normalized_edges, "k": c}
    IndependentSet.validate(target_instance)
    return target_instance

