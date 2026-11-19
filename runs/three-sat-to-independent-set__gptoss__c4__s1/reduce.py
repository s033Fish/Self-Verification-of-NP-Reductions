"""Reduction from 3‑SAT to Independent Set.

The source problem is :class:`ThreeSat` (see ``problems.py``).  An instance is a
dictionary ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}`` where each
clause contains exactly three literals on distinct variables.

The target problem is :class:`IndependentSet`.  An instance is a dictionary
``{"n": n, "edges": [[u, v], ...], "k": k}`` describing an undirected graph
with vertices ``0..n‑1`` and a target size ``k``.

Classic reduction:

* For each clause we create a *clique* of three vertices – one vertex per
  literal.  Because the three vertices are pairwise adjacent, any independent
  set can contain **at most** one vertex from a clause.
* Vertices belonging to different clauses are connected whenever the
  corresponding literals are complementary (``x`` vs ``-x``).  This forbids the
  independent set from picking two literals that cannot be simultaneously true.
* We ask for an independent set of size equal to the number of clauses.  Such a
  set must therefore contain exactly one vertex from each clause and no two of
  them are complementary – which directly yields a satisfying assignment.

The reduction runs in polynomial time: the graph has ``3 * C`` vertices where
``C`` is the number of clauses, and we add at most ``3*C`` intra‑clause edges
plus ``O(C^2)`` inter‑clause edges.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, IndependentSet


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeSat`` format.

    Returns
    -------
    dict
        An ``IndependentSet`` instance such that the answer to the new
        instance is *yes* iff the original 3‑SAT instance is satisfiable.
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # input is malformed.
    ThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge‑case: an empty formula is always satisfiable.  We can return any
    # graph with k = 0 because k <= 0 is automatically a yes‑instance.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Assign a vertex id to every literal in every clause.
    # vertex_id = clause_index * 3 + position_in_clause (0,1,2)
    vertex_literal: List[int] = []  # index -> literal (e.g., -3)
    for clause in clauses:
        for lit in clause:
            vertex_literal.append(lit)

    n = len(vertex_literal)  # = 3 * num_clauses
    edges: List[List[int]] = []
    seen = set()  # to avoid duplicate edges

    # 1. Intra‑clause edges – make each clause a triangle (3‑clique).
    for ci in range(num_clauses):
        base = ci * 3
        trio = [base, base + 1, base + 2]
        for i in range(3):
            for j in range(i + 1, 3):
                u, v = trio[i], trio[j]
                edges.append([u, v])
                seen.add(frozenset((u, v)))

    # 2. Inter‑clause edges for complementary literals.
    for u in range(n):
        lit_u = vertex_literal[u]
        for v in range(u + 1, n):
            # Skip if u and v belong to the same clause – already connected.
            if u // 3 == v // 3:
                continue
            lit_v = vertex_literal[v]
            if lit_u == -lit_v:
                key = frozenset((u, v))
                if key not in seen:
                    edges.append([u, v])
                    seen.add(key)

    k = num_clauses
    result = {"n": n, "edges": edges, "k": k}
    # Validate the produced target instance.
    IndependentSet.validate(result)
    return result

