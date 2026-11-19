"""Reduction from 3‑SAT to Independent Set.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with the
instance format:

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer ``+v`` (variable *v* is true) or
``-v`` (variable *v* is false).  Every clause contains exactly three
different variables.

The target problem is ``IndependentSet`` with instance format:

    {"n": n, "edges": [[u, v], ...], "k": k}

The reduction constructs a graph that contains a triangle for each clause
and connects contradictory literals across different clauses.  The graph
has an independent set of size at least ``k = number_of_clauses`` iff the
original 3‑SAT formula is satisfiable.

The construction is classic and runs in polynomial time:

* For each clause *C_i* we create three vertices, one for each literal.
* The three vertices of a clause are pairwise adjacent – they form a
  3‑clique.  Consequently an independent set can contain at most one
  vertex from each clause.
* For any two vertices belonging to different clauses, we add an edge if
  their literals are complementary, i.e. they refer to the same variable
  with opposite signs (``+v`` vs ``-v``).  This prevents selecting both a
  literal and its negation in the independent set.

If the formula is satisfiable, pick a true literal from each clause; the
corresponding vertices are pairwise non‑adjacent, giving an independent set
of size ``#clauses``.  Conversely, any independent set of that size must
contain exactly one vertex from each clause and cannot contain contradictory
literal pairs, yielding a satisfying assignment.

Edge cases:
  * An empty list of clauses is always satisfiable.  We return a graph with
    ``n = 0`` vertices, no edges, and ``k = 0`` – a trivial yes‑instance.

The ``reduce`` function below follows this specification and does not rely
on any external solvers.
"""

from typing import Dict, List, Tuple


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        in the problem statement.

    Returns
    -------
    dict
        An Independent Set instance ``{"n": n, "edges": [...], "k": k}``.
    """

    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Edge case: no clauses → trivially satisfiable.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Assign a vertex id to each literal of each clause.
    # vertices_info maps vertex id -> (clause_index, literal)
    vertices_info: List[Tuple[int, int]] = []  # (clause_idx, literal)
    for ci, clause in enumerate(clauses):
        # According to the specification each clause has exactly three literals.
        for lit in clause:
            vertices_info.append((ci, lit))

    n = len(vertices_info)  # should be 3 * num_clauses
    edges_set = set()

    # 1. Add edges inside each clause to form a triangle.
    for ci in range(num_clauses):
        # vertex ids for this clause are consecutive in the order we added them.
        base = ci * 3
        v0, v1, v2 = base, base + 1, base + 2
        for u, v in ((v0, v1), (v0, v2), (v1, v2)):
            if u > v:
                u, v = v, u
            edges_set.add((u, v))

    # 2. Add edges between contradictory literals from different clauses.
    # Iterate over all pairs of vertices from different clauses.
    for i in range(n):
        ci_i, lit_i = vertices_info[i]
        for j in range(i + 1, n):
            ci_j, lit_j = vertices_info[j]
            if ci_i == ci_j:
                continue  # same clause already handled
            # Literals are contradictory if they refer to same variable with opposite sign.
            # Since literals are encoded as +v or -v, they are opposite when lit_i == -lit_j.
            if lit_i == -lit_j:
                u, v = i, j
                if u > v:
                    u, v = v, u
                edges_set.add((u, v))

    # Convert edge set to required list format.
    edges: List[List[int]] = [[u, v] for (u, v) in sorted(edges_set)]

    # The required independent set size is the number of clauses.
    k = num_clauses

    return {"n": n, "edges": edges, "k": k}

