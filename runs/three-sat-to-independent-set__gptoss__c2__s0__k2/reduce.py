"""Reduction from 3‑SAT to Independent Set.

The source problem is ``ThreeSat`` with instances of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer: a positive value ``v`` denotes the
literal *x_v* (variable ``v`` set to ``True``) and a negative value ``-v``
denotes the literal *¬x_v*.

The target problem is ``IndependentSet`` with instances of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

The reduction constructs a graph that contains a triangle for each clause
and connects contradictory literals across clauses.  An independent set of
size at least ``k`` (where ``k`` is the number of clauses) corresponds
exactly to a satisfying assignment of the formula.

The construction is classic and runs in polynomial time.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
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
        The returned instance is a *yes* instance iff the original 3‑SAT
        instance is satisfiable.
    """

    num_vars = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Edge case: no clauses – the formula is always satisfiable.  We can
    # return a trivial graph with k = 0 (always a yes instance).
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Assign a unique vertex id to each literal occurrence.
    # Vertex ids are 0 .. 3*num_clauses-1.
    vertex_of: List[List[int]] = []  # vertex_of[clause_index][pos] = vertex id
    literal_of: List[List[int]] = []  # store the literal for each vertex
    for ci, clause in enumerate(clauses):
        # Each clause is guaranteed to have exactly three literals.
        if len(clause) != 3:
            # Defensive: if the input violates the spec we still handle it.
            raise ValueError("Each clause must contain exactly three literals")
        clause_vertices = []
        clause_literals = []
        for lit in clause:
            vid = ci * 3 + len(clause_vertices)
            clause_vertices.append(vid)
            clause_literals.append(lit)
        vertex_of.append(clause_vertices)
        literal_of.append(clause_literals)

    edges_set = set()

    # 1. Add edges forming a triangle inside each clause (no two literals of
    # the same clause can both be chosen).
    for verts in vertex_of:
        a, b, c = verts
        for u, v in ((a, b), (a, c), (b, c)):
            if u > v:
                u, v = v, u
            edges_set.add((u, v))

    # 2. Add edges between complementary literals across different clauses.
    # Build a map from variable to lists of (sign, vertex).
    var_to_pos: Dict[int, List[int]] = {}
    var_to_neg: Dict[int, List[int]] = {}
    for ci, lits in enumerate(literal_of):
        for pos, lit in enumerate(lits):
            vid = vertex_of[ci][pos]
            var = abs(lit)
            if lit > 0:
                var_to_pos.setdefault(var, []).append(vid)
            else:
                var_to_neg.setdefault(var, []).append(vid)

    for var in range(1, num_vars + 1):
        pos_list = var_to_pos.get(var, [])
        neg_list = var_to_neg.get(var, [])
        for u in pos_list:
            for v in neg_list:
                # Edge between complementary literals.
                a, b = (u, v) if u < v else (v, u)
                edges_set.add((a, b))

    # Convert edge set to required list format.
    edges = [[u, v] for (u, v) in sorted(edges_set)]

    n = 3 * num_clauses
    k = num_clauses
    return {"n": n, "edges": edges, "k": k}

