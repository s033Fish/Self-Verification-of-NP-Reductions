"""Reduction from 3‑SAT to Independent Set.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with the
instance format ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.  A literal is
represented by a signed integer: ``+v`` (or just ``v``) means the variable *v*
is true, ``-v`` means it is false.

The target problem is ``IndependentSet`` with the instance format
``{"n": n, "edges": [[u, v], ...], "k": k}``.  The reduction must produce a
graph that has an independent set of size *k* (the number of clauses) iff the
3‑SAT formula is satisfiable.

Standard reduction:
    * For each clause create a triangle of three vertices – one vertex for each
      literal in the clause.  The triangle ensures that an independent set can
      contain **at most one** vertex from each clause.
    * Connect vertices that correspond to complementary literals (e.g. ``x``
      and ``¬x``) across the whole graph.  This guarantees that the independent
      set cannot pick both a literal and its negation.

If the formula is satisfiable, we can pick, for every clause, the vertex that
represents a true literal under a satisfying assignment.  No two chosen
vertices are adjacent, giving an independent set of size equal to the number of
clauses.  Conversely, any independent set of that size must contain exactly one
vertex from each clause, and the selected literals cannot conflict, yielding a
consistent satisfying assignment.

The implementation below follows this construction and runs in polynomial time
with respect to the size of the 3‑SAT instance.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Set


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        in the problem statement.

    Returns
    -------
    dict
        An Independent Set instance ``{"n": n, "edges": [...], "k": k}``.
    """

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)
    # The target requires k = number of clauses (size of independent set we
    # aim to achieve).
    k = num_clauses

    # Assign a unique vertex id to each literal occurrence.
    # vertex_id = clause_index * 3 + position_in_clause (0,1,2)
    n = num_clauses * 3
    edges_set: Set[Tuple[int, int]] = set()

    # Helper to add an undirected edge without duplicates.
    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        a, b = (u, v) if u < v else (v, u)
        edges_set.add((a, b))

    # 1. Add triangle edges inside each clause.
    for ci, clause in enumerate(clauses):
        # Expect exactly three literals; if not, we still handle whatever is
        # provided (the source validator guarantees three distinct literals).
        base = ci * 3
        verts = [base + i for i in range(len(clause))]
        for i in range(len(verts)):
            for j in range(i + 1, len(verts)):
                add_edge(verts[i], verts[j])

    # 2. Connect complementary literals across clauses.
    # Build a map from (var, sign) to list of vertex ids.
    # sign == True for positive literal, False for negative.
    pos_map: Dict[int, List[int]] = {}
    neg_map: Dict[int, List[int]] = {}

    for ci, clause in enumerate(clauses):
        base = ci * 3
        for offset, lit in enumerate(clause):
            # ``lit`` may be an int (e.g., -3) or a string like "-3".
            if isinstance(lit, str):
                lit_int = int(lit)
            else:
                lit_int = int(lit)
            var = abs(lit_int)
            vertex = base + offset
            if lit_int > 0:
                pos_map.setdefault(var, []).append(vertex)
            else:
                neg_map.setdefault(var, []).append(vertex)

    for var in set(pos_map.keys()) | set(neg_map.keys()):
        pos_vertices = pos_map.get(var, [])
        neg_vertices = neg_map.get(var, [])
        for u in pos_vertices:
            for v in neg_vertices:
                add_edge(u, v)

    # Convert edge set to required list format.
    edges = [[u, v] for (u, v) in edges_set]

    return {"n": n, "edges": edges, "k": k}

