"""Reduction from 3‑SAT to Independent Set.

Implements the classic polynomial‑time reduction used in complexity theory:

* For each clause we create three vertices, one per literal, and connect them
  into a triangle.  This forces any independent set to pick at most one
  literal from each clause.
* For any two vertices belonging to different clauses we add an edge if the
  corresponding literals are complementary (e.g. ``x`` and ``¬x``).  This
  prevents the independent set from selecting contradictory assignments.
* The parameter ``k`` is set to the number of clauses.  An independent set of
  size ``k`` therefore corresponds to a truth assignment that satisfies the
  original formula.

The implementation follows the specification of the ``ThreeSat`` and
``IndependentSet`` classes defined in *problems.py*.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import ThreeSat, IndependentSet


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary representing a 3‑SAT formula as defined by
        :class:`ThreeSat`.

    Returns
    -------
    dict
        An ``IndependentSet`` instance ``{"n": n, "edges": [...], "k": k}``.
    """

    # Validate the source instance – raises InvalidInstance on malformed input.
    ThreeSat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case: formula with no clauses – always satisfiable.
    if num_clauses == 0:
        # Independent Set with k=0 is trivially yes.
        return {"n": 0, "edges": [], "k": 0}

    # Assign a unique vertex identifier to each literal of each clause.
    # vertex_of[ci][li] gives the vertex id for clause ci, literal position li.
    vertex_of: List[List[int]] = []
    next_vid = 0
    for _ in clauses:
        vertex_of.append([next_vid, next_vid + 1, next_vid + 2])
        next_vid += 3
    n = next_vid

    edges_set: set[Tuple[int, int]] = set()

    # 1. Add triangle edges inside each clause (force at most one literal).
    for verts in vertex_of:
        a, b, c = verts
        for u, v in ((a, b), (a, c), (b, c)):
            if u > v:
                u, v = v, u
            edges_set.add((u, v))

    # 2. Add conflict edges for complementary literals across different clauses.
    # Gather information about each literal.
    lit_info: List[Tuple[int, int, int, int]] = []  # (clause_idx, literal_idx, literal, vertex_id)
    for ci, clause in enumerate(clauses):
        for li, literal in enumerate(clause):
            lit_info.append((ci, li, literal, vertex_of[ci][li]))

    for i in range(len(lit_info)):
        ci, li, lit_i, vid_i = lit_info[i]
        for j in range(i + 1, len(lit_info)):
            cj, lj, lit_j, vid_j = lit_info[j]
            if ci == cj:
                # Same clause already connected by a triangle.
                continue
            if lit_i == -lit_j:
                u, v = vid_i, vid_j
                if u > v:
                    u, v = v, u
                edges_set.add((u, v))

    # Convert the set of edges to the list format required by IndependentSet.
    edges = [[u, v] for (u, v) in sorted(edges_set)]

    # Parameter k equals the number of clauses.
    k = num_clauses

    result = {"n": n, "edges": edges, "k": k}
    # Validate the constructed target instance.
    IndependentSet.validate(result)
    return result

