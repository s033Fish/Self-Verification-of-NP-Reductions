"""Reduction from SAT to Independent Set.

The source problem is defined by :class:`Sat` in ``problems.py`` and the
target problem by :class:`IndependentSet`.  Both classes provide a
``validate`` classmethod that raises :class:`InvalidInstance` if the input
does not conform to the format described in the docstring.

The classic polynomial‑time reduction creates a vertex for each literal
occurrence.  Vertices belonging to the same clause form a clique (so an
independent set can contain at most one literal from each clause).  In
addition, vertices that represent complementary literals (e.g. ``+x`` and
``-x``) are connected by an edge, guaranteeing that a satisfying
assignment never selects both a variable and its negation.

For a formula with ``c`` clauses we ask whether the constructed graph has
an independent set of size at least ``c``.  Selecting one vertex from each
clique yields a truth assignment that satisfies the formula, and any
independent set of size ``c`` yields a satisfying assignment.

Edge cases:
* If the formula contains no clauses, it is trivially satisfiable.  The
  reduction returns an empty graph with ``k = 0`` – independent‑set is
  always yes for ``k <= 0``.
* If a clause is empty, the formula is unsatisfiable.  The reduction will
  still set ``k`` to the total number of clauses but the empty clause
  contributes no vertices, making it impossible to obtain an independent
  set of size ``k``.

The function runs in time polynomial in the size of the SAT instance.
"""

from __future__ import annotations

from typing import List, Tuple, Dict, Set

from problems import Sat, IndependentSet, InvalidInstance


def _clause_vertices(clauses: List[List[int]]) -> Tuple[int, List[List[int]]]:
    """Assign a unique vertex id to each literal occurrence.

    Returns the total number of vertices and a parallel list ``v_ids``
    where ``v_ids[i][j]`` is the vertex id of the *j*‑th literal in clause
    *i*.
    """
    v_ids: List[List[int]] = []
    current = 0
    for clause in clauses:
        ids = []
        for _ in clause:
            ids.append(current)
            current += 1
        v_ids.append(ids)
    return current, v_ids


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
        An Independent Set instance ``{"n": n, "edges": [...], "k": k}``
        such that the answer to the SAT instance is *yes* iff the answer to
        the Independent Set instance is *yes*.
    """
    # Validate the source instance.
    Sat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case – no clauses.
    if num_clauses == 0:
        # An empty graph with k = 0 satisfies the Independent Set yes‑case.
        return {"n": 0, "edges": [], "k": 0}

    # Assign vertex ids.
    n, clause_vertex_ids = _clause_vertices(clauses)

    edges_set: Set[Tuple[int, int]] = set()

    # 1. Clique edges inside each clause.
    for ids in clause_vertex_ids:
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                u, v = ids[i], ids[j]
                edges_set.add((u, v) if u < v else (v, u))

    # 2. Complementary literal edges across clauses.
    # Build a mapping from (variable, sign) to list of vertex ids.
    # sign: True for positive, False for negative.
    lit_map: Dict[Tuple[int, bool], List[int]] = {}
    for ci, clause in enumerate(clauses):
        for li, literal in enumerate(clause):
            var = abs(literal)
            sign = literal > 0
            vid = clause_vertex_ids[ci][li]
            lit_map.setdefault((var, sign), []).append(vid)

    # For each variable, connect every positive occurrence to every negative
    # occurrence.
    for var in range(1, instance["num_vars"] + 1):
        pos = lit_map.get((var, True), [])
        neg = lit_map.get((var, False), [])
        for u in pos:
            for v in neg:
                edges_set.add((u, v) if u < v else (v, u))

    # Convert edge set to required list format.
    edges = [[u, v] for (u, v) in edges_set]

    # Build the target instance.
    target_instance = {"n": n, "edges": edges, "k": num_clauses}
    # Validate the target instance before returning.
    IndependentSet.validate(target_instance)
    return target_instance

