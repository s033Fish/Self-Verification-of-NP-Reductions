"""Reduction from 3‑SAT to Dominating Set.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with the
instance format:

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer ``+v`` (variable *v* is true) or ``-v``
(variable *v* is false).  Every clause contains exactly three literals on
distinct variables.

The target problem is ``DominatingSet`` with the instance format:

    {"n": n, "edges": [[u, v], ...], "k": k}

Vertices are numbered ``0 … n‑1`` and the edges are undirected.

We implement the classic polynomial‑time reduction that maps a 3‑CNF formula
``F`` to a graph ``G`` such that ``F`` is satisfiable iff ``G`` has a dominating
set of size at most ``m`` (the number of variables).  The construction is:

* For each variable ``x_i`` create two vertices ``x_i`` (true) and ``¬x_i``
  (false) and connect them with an edge.  Selecting one of the two vertices
  dominates both, representing the truth assignment of the variable.
* For each clause ``C_j`` create a vertex ``c_j`` and connect it to the three
  literal vertices that appear in the clause.

If a dominating set ``D`` has size ≤ ``m`` it must contain exactly one vertex
from each variable pair (otherwise the two vertices of the pair could not be
 dominated).  Consequently ``|D| = m`` and each clause vertex must be adjacent
to a selected literal vertex, which corresponds to the clause being satisfied.
Conversely, a satisfying assignment selects one literal per variable; those
vertices form a dominating set of size ``m``.

The reduction runs in time linear in the size of the formula.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeSat instance to a DominatingSet instance.

    Parameters
    ----------
    instance: dict
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``

    Returns
    -------
    dict
        ``{"n": n, "edges": [[u, v], ...], "k": k}`` where ``k = m``.
    """
    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Vertex numbering:
    #   For variable i (1‑based) we allocate two vertices:
    #       true  -> 2*(i-1)
    #       false -> 2*(i-1) + 1
    #   Clause vertices start after the 2*m variable vertices.
    var_true = lambda i: 2 * (i - 1)
    var_false = lambda i: 2 * (i - 1) + 1

    edges: List[List[int]] = []

    # Variable edges (pairwise connection)
    for i in range(1, m + 1):
        edges.append([var_true(i), var_false(i)])

    # Clause vertices and their connections to literals
    clause_offset = 2 * m
    for idx, clause in enumerate(clauses):
        clause_vertex = clause_offset + idx
        for lit in clause:
            var = abs(lit)
            if var == 0 or var > m:
                # Defensive: ignore malformed literals – the validator in
                # ``problems.py`` would reject such instances anyway.
                continue
            literal_vertex = var_true(var) if lit > 0 else var_false(var)
            edges.append([clause_vertex, literal_vertex])

    n = 2 * m + len(clauses)
    k = m

    # Ensure edges are stored with the smaller endpoint first (optional but
    # keeps the representation canonical).
    canonical_edges = []
    seen = set()
    for u, v in edges:
        if u == v:
            # No self‑loops in the definition of Dominating Set.
            continue
        a, b = (u, v) if u < v else (v, u)
        if (a, b) not in seen:
            seen.add((a, b))
            canonical_edges.append([a, b])

    return {"n": n, "edges": canonical_edges, "k": k}

