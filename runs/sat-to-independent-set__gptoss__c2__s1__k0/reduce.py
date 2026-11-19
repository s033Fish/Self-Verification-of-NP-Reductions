"""Reduction from SAT (CNF satisfiability) to Independent Set.

The source problem **Sat** is defined in ``problems.py`` with the following
instance format::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

where a *literal* is an integer ``+v`` (variable *v* true) or ``-v`` (variable
*v* false).  A clause is a list of literals; the list may be empty.  The formula
is satisfiable iff there exists a truth assignment that makes each clause
contain at least one true literal.

The target problem **IndependentSet** expects an instance of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

with vertices ``0..n-1`` and undirected edges ``[u, v]`` (``u != v``).  The
answer is *yes* iff the graph contains an independent set of size **at least**
``k``.

We implement the classic polynomial‑time reduction:

* For each clause ``C_i`` we create a *clique* of vertices, one vertex for each
  literal occurring in the clause.  Because the vertices of a clause form a
  clique, any independent set can contain **at most one** vertex from each clause.
* For two vertices belonging to *different* clauses we add an edge exactly when
  the corresponding literals are complementary (e.g. ``+x`` and ``-x``).  Such
  vertices cannot simultaneously belong to an independent set because they would
  force variable ``x`` to be both true and false.

With this construction, an independent set of size equal to the number of
clauses selects one *non‑conflicting* literal from each clause, which directly
encodes a satisfying assignment.  Conversely, any satisfying assignment yields
such an independent set.

Edge cases handled:
* **No clauses** – the SAT instance is trivially satisfiable.  We output a
  graph with ``n = 0`` vertices, no edges and ``k = 0`` (always yes).
* **Empty clause** – a clause with zero literals makes the formula unsatisfiable.
  Our construction creates a clause with no vertices, so the maximum possible
  independent set size is strictly less than the number of clauses, yielding a
  *no* answer.

The function ``reduce`` runs in time linear in the size of the SAT instance
(``O(total_literals^2)`` in the worst case due to clique edge generation, which
is polynomial).  It does **not** call any solver.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def reduce(sat_instance: Dict) -> Dict:
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    sat_instance: dict
        Instance of the SAT problem as described in the module docstring.

    Returns
    -------
    dict
        Instance of the Independent Set problem.  The returned instance
        satisfies ``is_yes(independent_set_instance)`` iff the original SAT
        instance is satisfiable.
    """

    clauses: List[List[int]] = sat_instance.get("clauses", [])
    num_clauses = len(clauses)

    # Trivial case: no clauses -> always satisfiable.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Assign a unique vertex id to each literal occurrence.
    # Mapping: (clause_index, position_in_clause) -> vertex_id
    vertex_id = 0
    clause_vertex_ids: List[List[int]] = []  # parallel to clauses
    literal_of_vertex: List[int] = []  # store literal for each vertex id
    for ci, clause in enumerate(clauses):
        current_ids: List[int] = []
        for lit in clause:
            current_ids.append(vertex_id)
            literal_of_vertex.append(lit)
            vertex_id += 1
        clause_vertex_ids.append(current_ids)

    n = vertex_id
    edges_set: set[Tuple[int, int]] = set()

    # 1. Add edges inside each clause to form a clique.
    for ids in clause_vertex_ids:
        l = len(ids)
        for i in range(l):
            for j in range(i + 1, l):
                u, v = ids[i], ids[j]
                edges_set.add((u, v) if u < v else (v, u))

    # 2. Add conflict edges between different clauses for complementary literals.
    # Build a map from (variable, sign) to list of vertex ids for fast lookup.
    # sign: True for positive literal, False for negative.
    pos_map: Dict[int, List[int]] = {}
    neg_map: Dict[int, List[int]] = {}
    for vid, lit in enumerate(literal_of_vertex):
        var = abs(lit)
        if lit > 0:
            pos_map.setdefault(var, []).append(vid)
        else:
            neg_map.setdefault(var, []).append(vid)

    # For each variable, connect every positive occurrence with every negative
    # occurrence (they belong to different clauses automatically because a clause
    # cannot contain both a literal and its negation without being trivially
    # satisfied – but even if it does, the intra‑clique edges already forbid taking
    # both).
    for var in set(pos_map.keys()) | set(neg_map.keys()):
        for u in pos_map.get(var, []):
            for v in neg_map.get(var, []):
                if u == v:
                    continue
                a, b = (u, v) if u < v else (v, u)
                edges_set.add((a, b))

    edges = [[u, v] for (u, v) in sorted(edges_set)]

    # The required independent set size is exactly the number of clauses.
    k = num_clauses

    return {"n": n, "edges": edges, "k": k}

# The module is intended to be imported by the evaluation harness; no top‑level
# execution is performed.
