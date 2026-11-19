"""Reduction from 3‑SAT to Independent Set.

The reduction follows the classic construction used in textbooks:

* For each clause we create a triangle (3 vertices, one per literal).
  The triangle forces an independent set to pick at most one literal from
  each clause.
* For any two literals that are complementary (e.g. ``x`` and ``-x``) we add
  an edge between the corresponding vertices.  This prevents the independent
  set from selecting both a variable and its negation.

If the original formula has *c* clauses, the constructed graph has ``n = 3*c``
vertices and we ask whether it contains an independent set of size at least
``k = c``.  A set of size ``c`` corresponds to picking exactly one literal per
clause, none of which conflict, which is precisely a satisfying assignment.

The implementation is straightforward and runs in polynomial time in the size
of the 3‑SAT instance.
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

from problems import ThreeSat, IndependentSet


def _clause_vertex_index(clause_idx: int, literal_idx: int) -> int:
    """Return the global vertex index for ``literal_idx`` of ``clause_idx``.

    Vertices are numbered consecutively per clause: clause 0 gets vertices
    0,1,2; clause 1 gets 3,4,5; and so on.
    """
    return clause_idx * 3 + literal_idx


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an Independent‑Set instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeSat`` format:
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.

    Returns
    -------
    dict
        An ``IndependentSet`` instance ``{"n": n, "edges": [...], "k": k}``.
    """
    # Validate the source instance – this will raise ``InvalidInstance`` if
    # the format is wrong.  The validation is inexpensive and helps catch bugs
    # early.
    ThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # No clauses → trivially satisfiable.  We return an empty graph with k=0.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    n_vertices = num_clauses * 3
    edges_set: Set[Tuple[int, int]] = set()

    # Helper to add an undirected edge without duplicates.
    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        a, b = (u, v) if u < v else (v, u)
        edges_set.add((a, b))

    # 1. Add edges inside each clause to form a triangle.
    for ci, clause in enumerate(clauses):
        # vertices for this clause are ci*3, ci*3+1, ci*3+2
        v0 = _clause_vertex_index(ci, 0)
        v1 = _clause_vertex_index(ci, 1)
        v2 = _clause_vertex_index(ci, 2)
        add_edge(v0, v1)
        add_edge(v0, v2)
        add_edge(v1, v2)

    # 2. Add edges between complementary literals across different clauses.
    #    We iterate over all pairs of clause‑literal occurrences.
    #    Since each clause has exactly three literals, a double loop over the
    #    vertices is acceptable (O(c^2) where c is the number of clauses).
    for ci1, clause1 in enumerate(clauses):
        for li1, lit1 in enumerate(clause1):
            v1 = _clause_vertex_index(ci1, li1)
            for ci2, clause2 in enumerate(clauses):
                # Avoid duplicate work and self‑comparison.
                if ci2 <= ci1:
                    continue
                for li2, lit2 in enumerate(clause2):
                    if lit1 == -lit2:  # complementary literals
                        v2 = _clause_vertex_index(ci2, li2)
                        add_edge(v1, v2)

    # Convert edge set to the required list format.
    edges = [[u, v] for (u, v) in sorted(edges_set)]

    # The target asks for an independent set of size at least the number of
    # clauses.
    k = num_clauses

    result = {"n": n_vertices, "edges": edges, "k": k}
    # Validate the target instance before returning.
    IndependentSet.validate(result)
    return result

