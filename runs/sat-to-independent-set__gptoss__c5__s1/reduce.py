"""Reduction from SAT to Independent Set.

The source problem is SAT (CNF satisfiability) as defined in ``problems.py``.
The target problem is Independent Set as defined in the same file.

For a given SAT instance we construct a graph G and an integer k such that
G has an independent set of size at least k **iff** the SAT formula is
 satisfiable.

Standard textbook reduction:

* For each clause C we create a vertex for every literal appearing in C.
* All vertices belonging to the same clause are made pairwise adjacent –
  this forces an independent set to contain at most one literal from each
  clause.
* Vertices representing complementary literals (e.g. ``x`` and ``-x``) are
  also made adjacent, even if they belong to different clauses.  This
  guarantees that an independent set cannot simultaneously select a literal
  and its negation.
* We set ``k`` to the number of clauses.  Selecting one vertex from each
  clause yields an independent set of size ``k`` exactly when the chosen
  literals are mutually non‑conflicting, i.e. they form a satisfying
  assignment.

Edge cases handled explicitly:

* **Empty formula** (no clauses) – always satisfiable.  We return a graph
  with ``k = 0`` which is trivially a yes‑instance for Independent Set.
* **Formula containing an empty clause** – unsatisfiable.  We construct a
  graph where ``k > n`` (e.g. ``n = 0, k = 1``) which is always a no‑instance.

The implementation runs in polynomial time with respect to the size of the
input formula.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import Sat, IndependentSet

def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``Sat`` format:
        ``{"num_vars": m, "clauses": [[literal, ...], ...]}``.

    Returns
    -------
    dict
        A dictionary adhering to the ``IndependentSet`` format:
        ``{"n": n, "edges": [[u, v], ...], "k": k}``.
    """
    # Validate the input according to the SAT specification.
    Sat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case 1: formula contains an empty clause -> unsatisfiable.
    if any(len(cl) == 0 for cl in clauses):
        # Return a trivially false Independent Set instance (k > n).
        return {"n": 0, "edges": [], "k": 1}

    # Edge case 2: no clauses -> always satisfiable.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Build vertices: one per literal occurrence.
    # Mapping from (clause_index, literal) -> vertex_id
    vertex_id = 0
    literal_vertices: List[Tuple[int, int]] = []  # (clause_index, literal)
    clause_vertices: List[List[int]] = []  # list of vertex ids per clause
    for ci, clause in enumerate(clauses):
        current_clause_ids: List[int] = []
        for lit in clause:
            literal_vertices.append((ci, lit))
            current_clause_ids.append(vertex_id)
            vertex_id += 1
        clause_vertices.append(current_clause_ids)

    n = vertex_id
    edges_set = set()

    # 1. Connect all pairs within the same clause (clique).
    for ids in clause_vertices:
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                u, v = ids[i], ids[j]
                edges_set.add(frozenset((u, v)))

    # 2. Connect complementary literals across different clauses.
    # Build a map from variable to vertices of positive and negative literals.
    pos_map: Dict[int, List[int]] = {}
    neg_map: Dict[int, List[int]] = {}
    for vid, (ci, lit) in enumerate(literal_vertices):
        var = abs(lit)
        if lit > 0:
            pos_map.setdefault(var, []).append(vid)
        else:
            neg_map.setdefault(var, []).append(vid)

    for var in set(pos_map.keys()) & set(neg_map.keys()):
        for u in pos_map[var]:
            for v in neg_map[var]:
                edges_set.add(frozenset((u, v)))

    # Convert edge set to required list format [u, v] with u < v for consistency.
    edges: List[List[int]] = []
    for e in edges_set:
        u, v = sorted(e)
        edges.append([u, v])

    # k is the number of clauses.
    k = num_clauses

    result = {"n": n, "edges": edges, "k": k}
    # Validate the produced instance against IndependentSet specification.
    IndependentSet.validate(result)
    return result

