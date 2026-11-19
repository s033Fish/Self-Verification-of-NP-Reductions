"""Reduction from SAT to Independent Set.

The source problem is SAT in CNF as described in ``problems.py``:

    {
        "num_vars": m,
        "clauses": [[literal, ...], ...]
    }

where a literal is an integer ``+v`` (meaning variable *v* is true) or
``-v`` (meaning variable *v* is false).  A clause may be empty, may contain
duplicate literals, and may contain both a variable and its negation.

The target problem is Independent Set with instance format:

    {
        "n": n,                # number of vertices (0‑based ids)
        "edges": [[u, v], ...], # undirected edges, each u!=v
        "k": k                 # size of independent set we ask for
    }

We implement the classic polynomial‑time reduction:

* For each clause we create a *clique* of vertices, one vertex for each
  literal occurrence.  Selecting at most one vertex from a clause is then
  enforced by the edges inside the clique.
* Between different clauses we add an edge for any pair of vertices whose
  literals are contradictory (e.g., ``+x`` and ``-x``).  This guarantees that
  a chosen set of vertices never contains both a variable and its negation.
* We ask for an independent set of size exactly the number of clauses ``k``.
  Such a set corresponds to picking one literal from each clause that are
  pairwise non‑contradictory, which yields a satisfying assignment.

Edge cases are handled explicitly:

* **No clauses** – the formula is trivially satisfiable.  We return a graph
  with ``n = 0`` vertices, ``k = 0`` (always a yes‑instance).
* **Empty clause present** – the formula is unsatisfiable.  We return a graph
  where ``k > n`` (e.g., ``n = 0``, ``k = 1``) which is always a no‑instance.

The implementation runs in time polynomial in the size of the SAT instance
(``O(L^2)`` where ``L`` is the total number of literal occurrences).
"""

from typing import Dict, List, Tuple


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        A SAT instance with keys ``"num_vars"`` and ``"clauses"`` as defined
        in the problem statement.

    Returns
    -------
    dict
        An Independent Set instance ``{"n": n, "edges": [...], "k": k}``
        that is a yes‑instance iff the original SAT instance is satisfiable.
    """

    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Edge case: formula with no clauses is always satisfiable.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Edge case: any empty clause makes the formula unsatisfiable.
    for cl in clauses:
        if len(cl) == 0:
            # Return a graph where k > n to guarantee a NO answer.
            return {"n": 0, "edges": [], "k": 1}

    # Build vertices: assign a unique id to each literal occurrence.
    # We keep a list of (clause_index, literal) for each vertex id.
    vertex_info: List[Tuple[int, int]] = []  # (clause_idx, literal)
    for ci, cl in enumerate(clauses):
        for lit in cl:
            vertex_info.append((ci, lit))

    n = len(vertex_info)
    k = num_clauses

    # Helper to add an undirected edge with u < v to the edge set.
    edges_set = set()
    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        if u > v:
            u, v = v, u
        edges_set.add((u, v))

    # 1. Add edges inside each clause to form a clique.
    start = 0
    for cl in clauses:
        sz = len(cl)
        # vertices for this clause are vertex IDs [start, start+sz)
        for i in range(start, start + sz):
            for j in range(i + 1, start + sz):
                add_edge(i, j)
        start += sz

    # 2. Add edges between contradictory literals from different clauses.
    # Build a mapping from (var, sign) to list of vertex ids.
    # sign: True for positive literal, False for negative.
    pos_map = {}
    neg_map = {}
    for vid, (_, lit) in enumerate(vertex_info):
        var = abs(lit)
        if lit > 0:
            pos_map.setdefault(var, []).append(vid)
        else:
            neg_map.setdefault(var, []).append(vid)

    # For each variable, connect every positive occurrence to every negative
    # occurrence (they belong to different clauses by construction of the
    # reduction; if they are in the same clause they are already connected via
    # the clique edges, but adding them again is harmless).
    for var in set(pos_map.keys()) | set(neg_map.keys()):
        pos_list = pos_map.get(var, [])
        neg_list = neg_map.get(var, [])
        for u in pos_list:
            for v in neg_list:
                add_edge(u, v)

    # Convert edge set to required list format.
    edges = [[u, v] for (u, v) in edges_set]

    return {"n": n, "edges": edges, "k": k}

