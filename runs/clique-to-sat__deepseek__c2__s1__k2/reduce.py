"""Polynomial-time reduction from Clique to SAT.

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
    Yes iff the graph on vertices 0..n-1 has a clique of at least k vertices.

SAT instance: {"num_vars": m, "clauses": [[literal, ...], ...]}
    Yes iff some assignment to variables 1..m satisfies every clause.

Reduction (standard Karp reduction)
-----------------------------------
If k <= 0 the answer is always yes, so return a trivially satisfiable
formula (no variables, no clauses).

If k > n the answer is always no, so return a formula containing the empty
clause, which is unsatisfiable.

Otherwise 1 <= k <= n.  Introduce a boolean variable x_{i,v} for each
position i in 1..k and each vertex v in 0..n-1, meaning "the i-th chosen
vertex is v".  Variable index: var(i, v) = (i - 1) * n + v + 1, so
num_vars = k * n.

Clauses:
  * For every position i, the clause [x_{i,0}, ..., x_{i,n-1}] forces at
    least one vertex to be chosen at position i.
  * For every position i and every pair u < v, the clause
    [-x_{i,u}, -x_{i,v}] forces at most one vertex at position i.
  * For every pair of positions i < j and every vertex v, the clause
    [-x_{i,v}, -x_{j,v}] forces the vertices chosen at distinct positions
    to be distinct.  (Without this, the same vertex could be reused, and
    the formula would be satisfiable even when no k-clique exists.)
  * For every pair of positions i < j and every non-edge {u, v} (u < v),
    the clauses [-x_{i,u}, -x_{j,v}] and [-x_{i,v}, -x_{j,u}] forbid the
    chosen vertices at positions i and j from being non-adjacent.

A satisfying assignment picks exactly one vertex per position (at least one
and at most one), all k chosen vertices are distinct, and every pair of
chosen vertices is joined by an edge: a k-clique.  Conversely, any k-clique
yields a satisfying assignment.  Since a clique of size at least k contains
one of size exactly k, this is equivalent to the "at least k" condition.

The formula has O(k * n^2 + k^2 * n + k^2 * n^2) clauses, each of length at
most n, so the reduction runs in polynomial time in the input size.
"""


def _var(position: int, vertex: int, n: int) -> int:
    """Variable for position (1-based) and vertex (0-based)."""
    return (position - 1) * n + vertex + 1


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge case of Clique: k <= 0 is always yes.
    if k <= 0:
        return {"num_vars": 0, "clauses": []}

    # Edge case: k > n is always no (also covers n == 0 with k >= 1).
    if k > n:
        return {"num_vars": 1, "clauses": [[]]}

    # Set of undirected edges as frozensets for O(1) membership tests.
    edge_set = {frozenset((u, v)) for u, v in edges}

    clauses = []

    # At least one vertex per position.
    for i in range(1, k + 1):
        clauses.append([_var(i, v, n) for v in range(n)])

    # At most one vertex per position.
    for i in range(1, k + 1):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var(i, u, n), -_var(i, v, n)])

    # The vertices chosen at two different positions must be distinct.
    for i in range(1, k + 1):
        for j in range(i + 1, k + 1):
            for v in range(n):
                clauses.append([-_var(i, v, n), -_var(j, v, n)])

    # Chosen vertices at distinct positions must be adjacent.
    for i in range(1, k + 1):
        for j in range(i + 1, k + 1):
            for u in range(n):
                for v in range(u + 1, n):
                    if frozenset((u, v)) not in edge_set:
                        clauses.append([-_var(i, u, n), -_var(j, v, n)])
                        clauses.append([-_var(i, v, n), -_var(j, u, n)])

    return {"num_vars": k * n, "clauses": clauses}
