"""Reduction from 3‑SAT to Clique.

The source problem is :class:`problems.ThreeSat` and the target is
``problems.Clique``.  The classic polynomial‑time reduction creates a vertex
for every literal in every clause.  Two vertices are connected by an edge iff
they belong to different clauses *and* the literals are not contradictory
(`v` and `-v`).  A satisfying assignment corresponds to picking exactly one
literal from each clause that are pairwise non‑contradictory – this is a clique
of size ``#clauses`` in the constructed graph.

Edge cases handled:
* An instance with **no clauses** is trivially satisfiable.  We map it to a
  graph with ``k = 0`` (any graph, even the empty graph, satisfies this).
* The reduction works for any number of clauses ≥ 1; the number of variables
  does not affect the construction.

The function runs in time O(c²) where ``c`` is the number of clauses (each
clause contributes exactly three vertices), which is polynomial in the size of
the 3‑SAT instance.
"""

from __future__ import annotations

from typing import List, Tuple

from problems import ThreeSat, Clique


def reduce(instance: dict) -> dict:
    """Reduce a 3‑SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the format of :class:`ThreeSat` – it must have
        keys ``"num_vars"`` and ``"clauses"``.

    Returns
    -------
    dict
        A dictionary adhering to the format of :class:`Clique` – keys ``"n"``,
        ``"edges"`` and ``"k"``.
    """
    # Validate the source instance – this will raise InvalidInstance if malformed.
    ThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case: empty formula – always satisfiable.  Choose k = 0 which is a
    # guaranteed yes instance for Clique.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Create a vertex for every literal in every clause.  We keep the vertices
    # in a flat list; the index of the vertex will be its identifier in the
    # Clique instance.
    vertices: List[Tuple[int, int]] = []  # (clause_index, literal)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertices.append((ci, lit))

    n = len(vertices)  # total number of vertices = 3 * num_clauses
    edges: List[List[int]] = []

    # Add an edge between every pair of vertices from different clauses unless
    # the literals are contradictory (i.e., one is the negation of the other).
    for i in range(n):
        ci, li = vertices[i]
        for j in range(i + 1, n):
            cj, lj = vertices[j]
            if ci == cj:
                # Vertices from the same clause must not be adjacent – we need
                # to pick exactly one literal per clause.
                continue
            if li == -lj:
                # Contradictory literals cannot both be true, so no edge.
                continue
            edges.append([i, j])

    # The target clique size is the number of clauses.
    k = num_clauses
    return {"n": n, "edges": edges, "k": k}

