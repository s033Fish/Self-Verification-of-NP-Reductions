"""Polynomial-time reduction from Vertex Cover to SAT.

SOURCE = VertexCover: {"n": n, "edges": [[u, v], ...], "k": k}
TARGET = Sat:         {"num_vars": m, "clauses": [[literal, ...], ...]}

Idea
----
Isolated vertices (degree 0) are never needed in a vertex cover, so first
restrict attention to the "active" vertices, i.e. those incident to at least
one edge.  There are at most 2*|edges| of them, so the size of the produced
formula depends only on the number of edges, not on the (possibly huge) value
of n.

After remapping the active vertices to 0..n'-1, introduce one boolean
variable x_v for each active vertex v (variable v+1 in the SAT instance),
meaning "v is in the cover".

* For every edge {u, v} add the clause (x_u OR x_v): every edge must be
  covered.

* Add an "at most k" cardinality constraint over x_0..x_{n'-1} using Sinz's
  sequential counter encoding.  Auxiliary variables s_{i,j} (1 <= i <= n',
  1 <= j <= k) mean "at least j of x_0..x_{i-1} are true".  The clauses are

      (A)  ~x_i OR s_{i,1}                       for 1 <= i <= n'
      (B)  ~s_{i-1,1} OR s_{i,1}                 for 2 <= i <= n'
      (C)  ~x_i OR ~s_{i-1,j-1} OR s_{i,j}       for 2 <= i <= n', 2 <= j <= k
      (D)  ~s_{i-1,j} OR s_{i,j}                 for 2 <= i <= n', 2 <= j <= k
      (E)  ~x_i OR ~s_{i-1,k}                    for k+1 <= i <= n'

  (E) forbids a (k+1)-st selected vertex, so the encoding is satisfiable
  exactly when at most k of the x_v are true.

Edge cases
----------
* k < 0: unsatisfiable (a single empty clause).
* k >= n' (all active vertices): the whole active set is a cover of size
  n' <= k, so only the edge clauses are needed (all x_v = true satisfies
  them).  In particular a graph with no edges has n' = 0 and is yes for
  every k >= 0 (empty cover), matching the definition.
* k == 0: no vertex may be selected, so add the unit clauses ~x_v.

The construction uses O(n'*k + |edges|) variables and clauses with
k < n' <= 2*|edges|, hence O(|edges|^2) total: polynomial time.
"""

from __future__ import annotations


def reduce(instance):
    edges = instance["edges"]
    k = instance["k"]

    # Only vertices incident to some edge can matter for a vertex cover.
    active = sorted({v for edge in edges for v in edge})
    n = len(active)
    index = {v: i for i, v in enumerate(active)}

    # Clause (x_u OR x_v) for every edge; variable v+1 represents vertex v.
    edge_clauses = [[index[u] + 1, index[v] + 1] for u, v in edges]

    if k < 0:
        # No cover can have negative size: emit an unsatisfiable formula.
        return {"num_vars": 0, "clauses": [[]]}

    if k >= n:
        # All active vertices form a cover of size n <= k; edge clauses are
        # satisfiable by setting every variable true.
        return {"num_vars": n, "clauses": edge_clauses}

    if k == 0:
        # At most zero vertices: force every x_v false.
        clauses = [[-(v + 1)] for v in range(n)] + edge_clauses
        return {"num_vars": n, "clauses": clauses}

    # 1 <= k < n: sequential counter encoding of "at most k".
    num_aux = n * k
    num_vars = n + num_aux

    def sid(i: int, j: int) -> int:
        """SAT variable id for auxiliary s_{i,j}, i in 1..n, j in 1..k."""
        return n + (i - 1) * k + j

    clauses = []

    # (A) x_i -> s_{i,1}   (x_i is variable i, i.e. active vertex i-1)
    for i in range(1, n + 1):
        clauses.append([-i, sid(i, 1)])

    # (B) s_{i-1,1} -> s_{i,1}
    for i in range(2, n + 1):
        clauses.append([-sid(i - 1, 1), sid(i, 1)])

    # (C) and (D)
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-i, -sid(i - 1, j - 1), sid(i, j)])
            clauses.append([-sid(i - 1, j), sid(i, j)])

    # (E) forbid a (k+1)-st true x_i
    for i in range(k + 1, n + 1):
        clauses.append([-i, -sid(i - 1, k)])

    clauses.extend(edge_clauses)
    return {"num_vars": num_vars, "clauses": clauses}
