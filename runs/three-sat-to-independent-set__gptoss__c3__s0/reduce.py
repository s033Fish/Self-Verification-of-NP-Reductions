"""Reduction from 3‑SAT to Independent Set.

The source problem is :class:`ThreeSat` (defined in ``problems.py``) and the
target problem is :class:`IndependentSet`.  The reduction follows the classic
construction used in textbooks:

* For each clause we create a triangle (3 vertices, all pairwise adjacent).
  The three vertices correspond to the three literals of the clause.
* Vertices that represent complementary literals – i.e. ``v`` and ``-v`` – are
  connected by an edge, even if they belong to different clauses.  Selecting
  both would correspond to setting a variable to both true and false, which is
  impossible.
* The parameter ``k`` of the Independent‑Set instance is set to the number of
  clauses.  An independent set of size ``k`` must therefore pick exactly one
  vertex from each clause triangle, and the complement‑literal edges guarantee
  that the chosen literals are mutually consistent.

Correctness sketch:

*If the 3‑SAT formula is satisfiable*: choose, for each clause, a literal that
 is true under a satisfying assignment.  The corresponding vertices are not
 adjacent (they belong to different clause triangles and are not complementary
 because a satisfying assignment never makes a variable both true and false).
 Hence they form an independent set of size ``k``.

*If the Independent‑Set instance has an independent set of size ``k``*: because
 each clause triangle is a 3‑clique, the independent set can contain at most
 one vertex from each triangle.  Achieving size ``k`` therefore means it picks
 exactly one vertex per clause.  The complement‑literal edges guarantee that no
 two selected literals conflict, so setting each selected literal to true
 yields a satisfying assignment.

The implementation runs in time linear in the number of clauses and the
 number of variables, which is polynomial in the size of the input instance.
"""

from __future__ import annotations

from typing import List, Tuple

from problems import ThreeSat, IndependentSet


def reduce(instance: dict) -> dict:
    """Reduce a 3‑SAT instance to an Independent‑Set instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the format of :class:`ThreeSat` – i.e.
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.

    Returns
    -------
    dict
        An Independent‑Set instance ``{"n": n, "edges": [...], "k": k}``.
    """
    # Validate the source instance using the provided class method.  This will
    # raise ``InvalidInstance`` if the format is wrong, matching the contract
    # expected by the surrounding harness.
    ThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case: no clauses → k = 0 and an empty graph (n = 0).
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Assign a vertex id to each literal in each clause.
    # vertex_id = clause_index * 3 + position_in_clause (0,1,2)
    vertex_literal: List[Tuple[int, int]] = []  # (vertex_id, literal)
    for ci, clause in enumerate(clauses):
        for pos, lit in enumerate(clause):
            vertex_id = ci * 3 + pos
            vertex_literal.append((vertex_id, lit))

    n = 3 * num_clauses
    edges_set = set()

    # 1. Add edges inside each clause (forming a triangle).
    for ci in range(num_clauses):
        base = ci * 3
        edges_set.update({frozenset((base, base + 1)), frozenset((base, base + 2)), frozenset((base + 1, base + 2))})

    # 2. Add edges between complementary literals across different clauses.
    # Build a mapping from variable to the vertices that represent its positive
    # and negative occurrences.
    pos_vertices: dict[int, List[int]] = {}
    neg_vertices: dict[int, List[int]] = {}
    for vid, lit in vertex_literal:
        var = abs(lit)
        if lit > 0:
            pos_vertices.setdefault(var, []).append(vid)
        else:
            neg_vertices.setdefault(var, []).append(vid)

    for var in set(pos_vertices) | set(neg_vertices):
        for p in pos_vertices.get(var, []):
            for n_vid in neg_vertices.get(var, []):
                edges_set.add(frozenset((p, n_vid)))

    # Convert edge set to the required list-of-lists format.
    edges = [list(edge) for edge in edges_set]

    return {"n": n, "edges": edges, "k": num_clauses}

