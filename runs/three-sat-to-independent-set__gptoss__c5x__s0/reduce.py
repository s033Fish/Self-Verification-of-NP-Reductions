"""Reduction from 3‑SAT to Independent Set.

The reduction follows the classic textbook construction:

* For each clause we create a triangle of three vertices, each vertex
  representing one literal of the clause.
* Vertices belonging to the same clause are pairwise adjacent – this
  guarantees that an independent set can contain **at most** one vertex
  from each clause.
* Vertices that correspond to complementary literals (e.g. ``x`` and
  ``-x``) are made adjacent as well.  This prevents the independent set
  from selecting contradictory literals.

If the original formula has *c* clauses, the graph has ``3*c`` vertices
and we ask for an independent set of size at least ``c``.  An
independent set of that size selects exactly one literal from every
clause, and the lack of edges between selected vertices guarantees that
the chosen literals are mutually consistent – which yields a satisfying
assignment for the formula.  Conversely, any satisfying assignment can be
translated into such an independent set.

The implementation is completely deterministic and runs in polynomial
time in the size of the 3‑SAT instance.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, IndependentSet


def _literal_vertex_index(clause_idx: int, literal_idx: int) -> int:
    """Return the vertex number for ``literal_idx`` (0‑2) inside ``clause_idx``.

    Vertices are numbered consecutively: clause 0 gets vertices 0,1,2;
    clause 1 gets 3,4,5; and so on.
    """
    return 3 * clause_idx + literal_idx


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeSat`` format.

    Returns
    -------
    dict
        A dictionary adhering to the ``IndependentSet`` format such that
        the answer to the Independent Set instance is *yes* iff the
        answer to the original 3‑SAT instance is *yes*.
    """
    # Validate the source instance – this will raise ``InvalidInstance``
    # if the input is malformed.
    ThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case: no clauses – the formula is trivially satisfiable.  We
    # return an empty graph with k = 0 (always a yes instance).
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    edges: List[List[int]] = []
    # 1. Add edges inside each clause to form a triangle.
    for ci in range(num_clauses):
        v0 = _literal_vertex_index(ci, 0)
        v1 = _literal_vertex_index(ci, 1)
        v2 = _literal_vertex_index(ci, 2)
        edges.append([v0, v1])
        edges.append([v0, v2])
        edges.append([v1, v2])

    # 2. Add edges between complementary literals from different clauses.
    # Build a mapping from (variable, sign) to the vertex representing it.
    # sign is +1 for positive, -1 for negative.
    literal_to_vertex: Dict[tuple[int, int], List[int]] = {}
    for ci, clause in enumerate(clauses):
        for li, literal in enumerate(clause):
            var = abs(literal)
            sign = 1 if literal > 0 else -1
            key = (var, sign)
            literal_to_vertex.setdefault(key, []).append(_literal_vertex_index(ci, li))

    # For every variable, connect all vertices of opposite signs.
    for var in range(1, instance["num_vars"] + 1):
        pos_vertices = literal_to_vertex.get((var, 1), [])
        neg_vertices = literal_to_vertex.get((var, -1), [])
        for vp in pos_vertices:
            for vn in neg_vertices:
                edges.append([vp, vn])

    # The graph has exactly 3 * num_clauses vertices.
    n_vertices = 3 * num_clauses
    target_instance = {"n": n_vertices, "edges": edges, "k": num_clauses}

    # Validate the produced target instance before returning.
    IndependentSet.validate(target_instance)
    return target_instance

