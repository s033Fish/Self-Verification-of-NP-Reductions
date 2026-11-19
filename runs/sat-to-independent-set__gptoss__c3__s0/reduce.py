"""Reduction from SAT to Independent Set.

The source problem is SAT as defined in ``problems.Sat``.  An instance is a
dictionary ``{"num_vars": m, "clauses": [[l1, l2, ...], ...]}`` where each
literal is an integer ``+v`` (variable *v* is true) or ``-v`` (variable *v*
is false).  The target problem is Independent Set (``problems.IndependentSet``)
with instance format ``{"n": n, "edges": [[u, v], ...], "k": k}``.

Standard textbook reduction:

* For each clause create a *clique* containing a vertex for every literal in
  that clause.
* Connect two vertices from different clauses if the corresponding literals
  are complementary (i.e., they refer to the same variable with opposite
  polarity).
* Set ``k`` to the number of clauses.

If the original formula is satisfiable, we can pick one true literal from each
clause; the chosen vertices are pairwise non‑adjacent, giving an independent
set of size ``k``.  Conversely, an independent set of size ``k`` must contain
exactly one vertex from each clause (cliques forbid two from the same clause),
and the selected literals cannot be complementary, yielding a satisfying
assignment.

The reduction also correctly handles edge cases described in the problem
specifications:

* **No clauses** – the SAT instance is trivially satisfiable.  We return a
  graph with ``k = 0`` (any graph works; we choose an empty graph).
* **Empty clause** – such a formula is unsatisfiable.  The reduction creates a
  graph with ``n = 0`` and ``k`` equal to the number of clauses (which is at
  least one).  Because ``k > n``, the Independent Set instance is a definite
  *no* instance.
* **Zero variables** – handled automatically; literals are still validated by
  the source instance validator.

The implementation runs in time polynomial in the size of the SAT instance
(``O(total_literals^2)``) which is easily within the required bounds.
"""

from __future__ import annotations

from typing import List, Tuple, Set

from problems import Sat, IndependentSet

def reduce(instance: dict) -> dict:
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        A validated SAT instance (the caller may rely on ``Sat.validate``).

    Returns
    -------
    dict
        An Independent Set instance such that the answer to the SAT instance
        is *yes* iff the answer to the returned Independent Set instance is
        *yes*.
    """
    # Validate the source instance (will raise if malformed).
    Sat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case: formula with no clauses – always satisfiable.
    if num_clauses == 0:
        # Empty graph with k = 0 satisfies the Independent Set yes‑condition.
        return {"n": 0, "edges": [], "k": 0}

    # Edge case: any empty clause makes the formula unsatisfiable.
    if any(len(cl) == 0 for cl in clauses):
        # No vertices, but k > 0 ⇒ answer is always no.
        return {"n": 0, "edges": [], "k": num_clauses}

    # Build vertices: one per literal in each clause.
    # vertex_id will be assigned sequentially.
    vertex_ids: List[List[int]] = []  # parallel to clauses, stores ids per literal
    literals: List[int] = []  # literal value for each vertex id (index matched)
    current_id = 0
    for cl in clauses:
        ids_this_clause: List[int] = []
        for lit in cl:
            ids_this_clause.append(current_id)
            literals.append(lit)
            current_id += 1
        vertex_ids.append(ids_this_clause)

    n_vertices = current_id
    edges_set: Set[Tuple[int, int]] = set()

    # 1. Add edges inside each clause to form a clique.
    for ids in vertex_ids:
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                u, v = ids[i], ids[j]
                if u > v:
                    u, v = v, u
                edges_set.add((u, v))

    # 2. Add edges between complementary literals from different clauses.
    # We'll compare every pair of vertices from different clauses.
    # Since the number of vertices is modest for our test sizes, O(N^2) is fine.
    for ci, ids_i in enumerate(vertex_ids):
        for cj in range(ci + 1, len(vertex_ids)):
            ids_j = vertex_ids[cj]
            for u in ids_i:
                lit_u = literals[u]
                for v in ids_j:
                    lit_v = literals[v]
                    if lit_u == -lit_v:
                        a, b = (u, v) if u < v else (v, u)
                        edges_set.add((a, b))

    # Convert edge set to required list format.
    edges = [[u, v] for (u, v) in edges_set]

    return {"n": n_vertices, "edges": edges, "k": num_clauses}

