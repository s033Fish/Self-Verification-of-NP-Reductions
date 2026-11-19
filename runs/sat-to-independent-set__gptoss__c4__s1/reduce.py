"""Reduction from SAT to Independent Set.

The reduction follows the classic textbook construction:

* For each clause we create a *clique* of vertices, one vertex for each
  literal occurrence in the clause.
* Vertices belonging to different clauses are connected by an edge iff the
  corresponding literals are complementary (e.g., ``x`` and ``-x``).
* The target instance asks for an independent set of size at least ``k``
  where ``k`` is the number of clauses.

If the original CNF formula is satisfiable, we can pick a true literal from
each clause; the chosen vertices form an independent set of size ``k``.
Conversely, any independent set of size ``k`` must contain exactly one vertex
from each clause (because each clause's vertices form a clique) and cannot
contain complementary literals, which yields a satisfying assignment.

Edge‑case handling mirrors the specification in ``problems.py``:

* An empty formula (no clauses) is always satisfiable. The reduction returns
  a graph with ``k = 0`` – independent‑set instances with ``k <= 0`` are
  trivially yes.
* A formula containing an empty clause has no vertices for that clause but
  ``k`` counts the clause. Since the graph then has fewer vertices than
  ``k``, the independent‑set answer is ``no`` as required.
"""

from __future__ import annotations

from typing import List, Tuple, Dict, Set

from problems import Sat, IndependentSet


def _complement(lit: int) -> int:
    """Return the complementary literal of ``lit`` (e.g., 3 -> -3)."""
    return -lit


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the format of :class:`Sat` –
        ``{"num_vars": m, "clauses": [[literal, ...], ...]}``.

    Returns
    -------
    dict
        An Independent‑Set instance ``{"n": n, "edges": [[u, v], ...], "k": k}``.
    """
    # Validate input according to the problem definition.
    Sat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    k = len(clauses)  # target independent‑set size

    # Assign a unique vertex id to each literal occurrence.
    # Keep track of the literal (including sign) for each vertex.
    vertex_literal: List[int] = []  # index is vertex id, value is literal
    clause_vertices: List[List[int]] = []  # per‑clause list of vertex ids
    for clause in clauses:
        cur: List[int] = []
        for lit in clause:
            vid = len(vertex_literal)
            vertex_literal.append(lit)
            cur.append(vid)
        clause_vertices.append(cur)

    n = len(vertex_literal)
    edge_set: Set[frozenset[int]] = set()

    # 1. Add edges inside each clause to form a clique.
    for verts in clause_vertices:
        for i in range(len(verts)):
            for j in range(i + 1, len(verts)):
                edge_set.add(frozenset((verts[i], verts[j])))

    # 2. Add edges between complementary literals from different clauses.
    #    We compare every pair of vertices belonging to different clauses.
    #    Since the number of vertices is small for our test harness, a simple
    #    O(n^2) scan is acceptable and keeps the implementation clear.
    for c1_idx, verts1 in enumerate(clause_vertices):
        for c2_idx in range(c1_idx + 1, len(clause_vertices)):
            verts2 = clause_vertices[c2_idx]
            for v1 in verts1:
                lit1 = vertex_literal[v1]
                for v2 in verts2:
                    lit2 = vertex_literal[v2]
                    if lit1 == _complement(lit2):
                        edge_set.add(frozenset((v1, v2)))

    # Convert edge set to the required list format (ordered pairs).
    edges: List[List[int]] = [sorted(list(e)) for e in edge_set]

    result = {"n": n, "edges": edges, "k": k}
    # Validate the produced instance as an IndependentSet instance.
    IndependentSet.validate(result)
    return result

