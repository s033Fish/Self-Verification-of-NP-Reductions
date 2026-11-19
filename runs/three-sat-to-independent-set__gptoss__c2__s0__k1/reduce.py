"""Reduction from 3‑SAT to Independent Set.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with an
instance format:

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``l`` is an integer ``+v`` (variable *v* is true) or
``-v`` (variable *v* is false).  Every clause contains exactly three
distinct variables.

The target problem is ``IndependentSet`` with an instance format:

    {"n": n, "edges": [[u, v], ...], "k": k}

The reduction constructs, for each clause, a triangle of three vertices –
one for each literal.  Vertices belonging to the same clause are pairwise
adjacent, ensuring that any independent set can contain **at most one**
vertex from each clause.  Additionally, vertices whose literals are
negations of the same variable (e.g. ``+2`` and ``-2``) are connected across
clauses.  Selecting one vertex from each clause that are mutually non‑adjacent
corresponds exactly to a satisfying assignment of the original formula.

The reduction runs in polynomial time:
    * ``n = 3 * C`` where ``C`` is the number of clauses.
    * At most ``3*C choose 2`` edges are added – well within polynomial
      bounds.

The function ``reduce`` implements this transformation.  It handles the
edge case of an empty clause list (the formula is trivially satisfiable) by
returning a graph with ``k = 0`` which is always a yes‑instance for the
Independent Set problem.
"""

from typing import Dict, List, Tuple, Set


def reduce(instance: Dict) -> Dict:
    """Convert a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        in the problem statement.

    Returns
    -------
    dict
        An Independent Set instance with keys ``"n"``, ``"edges"`` and
        ``"k"``.
    """

    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Edge case: no clauses – the formula is always satisfiable.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Assign a vertex id to each literal occurrence.
    # vertex_id = clause_index * 3 + position_in_clause (0,1,2)
    n = 3 * num_clauses
    edges_set: Set[Tuple[int, int]] = set()

    # Helper to add an undirected edge with ordering u < v.
    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        if u > v:
            u, v = v, u
        edges_set.add((u, v))

    # 1. Connect vertices inside the same clause (forming a triangle).
    for ci, clause in enumerate(clauses):
        base = ci * 3
        # there should be exactly three literals, but we are tolerant.
        for i in range(3):
            for j in range(i + 1, 3):
                add_edge(base + i, base + j)

    # 2. Connect contradictory literals across different clauses.
    # Build a mapping from (variable, sign) to list of vertex ids.
    # sign: True for positive literal, False for negative.
    lit_to_vertices: Dict[Tuple[int, bool], List[int]] = {}
    for ci, clause in enumerate(clauses):
        for pos, lit in enumerate(clause):
            var = abs(lit)
            sign = lit > 0
            vid = ci * 3 + pos
            lit_to_vertices.setdefault((var, sign), []).append(vid)

    # For each variable, connect every positive occurrence with every negative
    # occurrence (if they belong to different clauses, the earlier triangle
    # edges already handle intra‑clause connections).
    for var in range(1, instance.get("num_vars", 0) + 1):
        pos_vertices = lit_to_vertices.get((var, True), [])
        neg_vertices = lit_to_vertices.get((var, False), [])
        for u in pos_vertices:
            for v in neg_vertices:
                add_edge(u, v)

    edges = [[u, v] for (u, v) in sorted(edges_set)]

    # The required independent set size is the number of clauses.
    k = num_clauses

    return {"n": n, "edges": edges, "k": k}

