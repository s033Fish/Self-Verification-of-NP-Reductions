"""Reduction from SAT (CNF satisfiability) to Independent Set.

The source problem (SAT) instances have the form::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

where a *literal* is an integer ``+v`` (meaning variable *v* is true) or
``-v`` (meaning variable *v* is false).  A clause is a list of literals –
the list may be empty, may contain duplicates, and may even contain both
``v`` and ``-v``.

The target problem (Independent Set) instances have the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

where vertices are numbered ``0 .. n-1`` and ``k`` is the required size of
the independent set.

The classic polynomial‑time reduction creates a vertex for each literal
occurring in a clause.  Vertices belonging to the *same* clause are made
pairwise adjacent (forming a clique).  Additionally, vertices that
represent complementary literals (e.g. ``+x`` and ``-x``) are connected –
these edges may appear between different clauses.  The resulting graph has
an independent set of size exactly the number of clauses *iff* the SAT
formula is satisfiable.

Edge cases handled explicitly:

* **No clauses** – the formula is trivially satisfiable.  We output a graph
  with ``k = 0`` (any graph works, we choose an empty graph).  Since
  ``k <= 0`` the Independent Set instance is a yes‑instance.
* **Empty clause** – such a clause can never be satisfied, so the SAT
  instance is a no‑instance.  We produce a graph where ``k > n`` (here
  ``n = 0`` and ``k = 1``), which is always a no‑instance for Independent
  Set.

The function ``reduce`` follows the description above and runs in time
polynomial in the size of the SAT instance.
"""

from typing import List, Dict, Tuple


def _complement(lit: int) -> int:
    """Return the complementary literal of ``lit``.

    ``lit`` is a signed integer where the sign indicates polarity.  The
    complement simply flips the sign while keeping the variable number.
    """
    return -lit


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        A SAT instance matching the format described in the module level
        docstring.

    Returns
    -------
    dict
        An Independent Set instance such that the answer to the returned
        instance is *yes* iff the answer to the input SAT instance is
        *yes*.
    """

    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Edge case: formula contains an empty clause → unsatisfiable.
    if any(len(cl) == 0 for cl in clauses):
        # Return a trivially false Independent Set instance: k > n.
        return {"n": 0, "edges": [], "k": 1}

    # Edge case: no clauses → always satisfiable.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Assign a unique vertex id to each literal occurrence.
    # Mapping: (clause_index, position_in_clause) -> vertex_id
    vertex_of: List[List[int]] = []  # same shape as clauses, stores ids
    next_id = 0
    for cl in clauses:
        ids_in_clause = []
        for _ in cl:
            ids_in_clause.append(next_id)
            next_id += 1
        vertex_of.append(ids_in_clause)

    n = next_id  # total number of vertices
    edges_set: set[Tuple[int, int]] = set()

    # 1. Add edges forming a clique inside each clause.
    for ids in vertex_of:
        sz = len(ids)
        for i in range(sz):
            for j in range(i + 1, sz):
                u, v = ids[i], ids[j]
                if u > v:
                    u, v = v, u
                edges_set.add((u, v))

    # 2. Add edges between complementary literals across different clauses.
    # Build a map from literal value to list of (clause_idx, vertex_id).
    lit_to_vertices: Dict[int, List[int]] = {}
    for cl_idx, cl in enumerate(clauses):
        for pos, lit in enumerate(cl):
            v_id = vertex_of[cl_idx][pos]
            lit_to_vertices.setdefault(lit, []).append(v_id)

    # For each literal, connect its vertices to vertices of its complement.
    for lit, verts in lit_to_vertices.items():
        comp = _complement(lit)
        if comp not in lit_to_vertices:
            continue
        comp_verts = lit_to_vertices[comp]
        for u in verts:
            for v in comp_verts:
                # Avoid self‑loops and duplicate edges.
                if u == v:
                    continue
                a, b = (u, v) if u < v else (v, u)
                edges_set.add((a, b))

    # Convert edge set to required list format.
    edges = [[u, v] for (u, v) in edges_set]

    return {"n": n, "edges": edges, "k": num_clauses}

