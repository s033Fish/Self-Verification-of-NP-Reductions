"""Polynomial-time reduction from 3-SAT (SOURCE) to Clique (TARGET).

Reduction (the classic Karp reduction)
--------------------------------------
Given a 3-SAT instance {"num_vars": m, "clauses": [[l1, l2, l3], ...]}:

* For every clause occurrence C_i and every literal l in C_i, create one
  vertex (i, l).  Thus there are 3 * len(clauses) vertices (each clause
  occurrence gets its own group, so duplicated clauses are handled
  correctly).
* Join two vertices (i, l) and (j, l') with an edge iff i != j (they come
  from different clause occurrences) and l and l' are not complementary
  (l != -l').  Literals inside one clause are never joined, and a vertex
  is never joined to a literal that contradicts it.
* Set k = number of clause occurrences.

Correctness
-----------
(=>) A satisfying assignment makes at least one literal true in every
clause.  Pick one true literal per clause occurrence; these vertices lie
in distinct groups and no two chosen literals are complementary (both
would be true, which is impossible), so they form a clique of size
len(clauses) = k.

(<=) A clique of size k must contain exactly one vertex from each of the
k clause groups (two vertices of the same group are never adjacent, and
there are only k groups).  Assign each variable the truth value that
makes the selected literal true; this is consistent because adjacent
vertices are never complementary, so no variable is forced both true and
false.  Every clause then has a true literal, so the formula is
satisfiable.

Edge cases
----------
* No clauses: k = 0 and the graph has no vertices.  Clique answers yes
  for k <= 0, matching the satisfiable empty formula.
* k <= 0 / k > n cannot arise here since k = number of clauses and
  n = 3 * number of clauses (for k > 0, n >= 3k > k).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: Any) -> dict:
    """Reduce a 3-SAT instance to a Clique instance.

    The returned instance is a valid Clique instance (vertices 0..n-1,
    simple undirected edge list, integer k) that is a yes-instance exactly
    when the input 3-SAT instance is satisfiable.
    """
    clauses = instance["clauses"]

    # One vertex per literal occurrence: vertex index -> literal value.
    literals: list[int] = []
    # Group (clause occurrence index) of each vertex.
    group: list[int] = []
    for clause_index, clause in enumerate(clauses):
        for literal in clause:
            literals.append(literal)
            group.append(clause_index)

    n = len(literals)

    # Join vertices from different clause groups with non-complementary
    # literals.  Iterating u < v produces each undirected edge once.
    edges: list[list[int]] = []
    for u in range(n):
        lu = literals[u]
        gu = group[u]
        for v in range(u + 1, n):
            if group[v] != gu and literals[v] != -lu:
                edges.append([u, v])

    k = len(clauses)

    return {"n": n, "edges": edges, "k": k}
