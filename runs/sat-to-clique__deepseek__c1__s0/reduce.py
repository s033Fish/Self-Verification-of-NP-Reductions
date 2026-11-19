"""Polynomial-time reduction from SAT to Clique.

Reduction (the classic Karp reduction):

  * For every clause and every literal occurrence in it, create one vertex.
    A vertex is labelled by its literal.
  * Join two vertices with an edge iff they come from *different* clauses
    and their literals are not complementary (i.e. not ``v`` and ``-v``).
  * Let ``k`` be the number of clauses.

Why it is correct:

  * A clique of size ``k`` must use exactly one vertex from each clause
    (there are no edges inside a clause, so at most one vertex per clause,
    and there are ``k`` clauses).  The chosen literals are pairwise
    non-contradictory, so setting each chosen literal to true gives a
    satisfying assignment (every clause contains its chosen true literal).
  * Conversely, if the formula is satisfiable, pick one true literal from
    each clause; these literals are pairwise non-contradictory, so the
    corresponding vertices form a clique of size ``k``.

Edge cases line up with the Clique definition:

  * No clauses  -> k = 0, which Clique always answers yes.
  * An empty clause contributes no vertex, so no clique can reach size k
    (k >= 1) and Clique answers no.
  * The maximum clique has at most one vertex per clause, hence size <= k,
    so "at least k" is equivalent to "exactly k".

The construction is polynomial: the number of vertices is the total number
of literal occurrences and the number of edges is at most quadratic in it.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Reduce a SAT instance to a Clique instance.

    ``instance`` is ``{"num_vars": m, "clauses": [[literal, ...], ...]}``.
    The result is ``{"n": n, "edges": [[u, v], ...], "k": k}``.
    """
    clauses = instance["clauses"]

    # One vertex per literal occurrence, remembering its literal value.
    literals: list[int] = []
    for clause in clauses:
        for literal in clause:
            literals.append(literal)

    n = len(literals)

    # Map each vertex to its clause index so we can forbid intra-clause edges.
    clause_of: list[int] = []
    for clause_index, clause in enumerate(clauses):
        clause_of.extend([clause_index] * len(clause))

    edges: list[list[int]] = []
    for u in range(n):
        lu = literals[u]
        cu = clause_of[u]
        for v in range(u + 1, n):
            # Different clauses and non-complementary literals.
            if cu != clause_of[v] and lu != -literals[v]:
                edges.append([u, v])

    return {"n": n, "edges": edges, "k": len(clauses)}
