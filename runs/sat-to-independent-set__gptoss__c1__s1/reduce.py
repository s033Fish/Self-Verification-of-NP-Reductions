"""Reduction from SAT (CNF) to Independent Set.

The source problem (SAT) instance format is a dictionary:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
where each literal is an integer +v (positive) or -v (negative) with
1 <= v <= m.  An empty list of clauses is trivially satisfiable, and a
clause that is the empty list [] is unsatisfiable.

The target problem (Independent Set) expects a dictionary:
    {"n": n, "edges": [[u, v], ...], "k": k}
where vertices are numbered 0..n-1, edges are undirected and listed
once, and the question is whether there exists an independent set of
size at least k.

Standard reduction:
  * For each literal occurring in a clause we create a vertex.
  * Vertices belonging to the same clause are made pairwise adjacent –
    this forces an independent set to pick at most one literal per clause.
  * Vertices representing complementary literals (v and -v) from *different*
    clauses are also made adjacent – this prevents picking contradictory
    assignments.
  * We ask for an independent set of size exactly the number of clauses
    (k = #clauses).  Such a set exists iff the formula is satisfiable.

Edge‑cases are handled explicitly so that the reduction preserves the
answer without relying on the construction above:
  * No clauses → SAT is yes.  We return the trivial Independent Set instance
    with k = 0 (always yes).
  * Any empty clause → SAT is no.  We return a graph with 0 vertices and
    k = 1 (k > n is automatically a no‑instance).

The implementation runs in polynomial time – the number of vertices is the
total number of literals across all clauses, and we add O(N^2) edges at
most, which is acceptable for the reduction.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A SAT instance respecting the format described in the module docstring.

    Returns
    -------
    dict
        An Independent Set instance whose yes‑answer matches the input's.
    """

    num_vars = instance.get("num_vars")  # not directly needed for reduction
    clauses: List[List[int]] = instance.get("clauses", [])

    # Edge case: formula with no clauses is always satisfiable.
    if len(clauses) == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Edge case: any empty clause makes the formula unsatisfiable.
    # We produce a graph with 0 vertices and k = 1 (> n) which is a guaranteed no.
    for cl in clauses:
        if len(cl) == 0:
            return {"n": 0, "edges": [], "k": 1}

    # Build vertices: one per literal occurrence.
    # We store for each vertex its clause index, variable index and sign.
    vertex_info: List[tuple[int, int, bool]] = []  # (clause_idx, var, sign)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            var = abs(lit)
            sign = lit > 0  # True for positive literal, False for negative
            vertex_info.append((ci, var, sign))

    n = len(vertex_info)
    edges: List[List[int]] = []

    # Helper to add an undirected edge without duplicates.
    # Since we generate edges in a deterministic order, we can simply append.
    def add_edge(u: int, v: int) -> None:
        if u > v:
            u, v = v, u
        edges.append([u, v])

    # 1. Connect vertices within the same clause (clique).
    # We'll collect vertex indices per clause first.
    clause_to_vertices: Dict[int, List[int]] = {}
    for idx, (ci, _var, _sign) in enumerate(vertex_info):
        clause_to_vertices.setdefault(ci, []).append(idx)

    for verts in clause_to_vertices.values():
        # add all unordered pairs
        for i in range(len(verts)):
            for j in range(i + 1, len(verts)):
                add_edge(verts[i], verts[j])

    # 2. Connect complementary literals across different clauses.
    # For each pair of vertices from different clauses, if they refer to the
    # same variable with opposite signs, add an edge.
    for i in range(n):
        ci_i, var_i, sign_i = vertex_info[i]
        for j in range(i + 1, n):
            ci_j, var_j, sign_j = vertex_info[j]
            if var_i == var_j and sign_i != sign_j:
                # They may already be connected via clause clique; adding a
                # duplicate edge would violate validation, so we check.
                # The only duplicate possibility is when the two vertices are
                # from the same clause, but that case has already been handled
                # and we skip because ci_i == ci_j would mean they are in the
                # same clause – we still need the edge, but it is already added.
                if ci_i != ci_j:
                    add_edge(i, j)

    k = len(clauses)
    return {"n": n, "edges": edges, "k": k}

