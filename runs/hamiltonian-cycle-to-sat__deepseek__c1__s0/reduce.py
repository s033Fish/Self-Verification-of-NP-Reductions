"""Polynomial-time reduction from Hamiltonian Cycle (undirected) to SAT.

Construction
------------
Let n = instance["n"].

If n <= 2 the graph can never have a Hamiltonian cycle, so we return a
trivially unsatisfiable formula (a single empty clause).

Otherwise introduce n*n boolean variables

    x[v][i]  <->  "vertex v is the i-th vertex of the cycle"   (0 <= v,i < n)

encoded as the integer variable  v*n + i + 1.

Clauses:
  (1) For every position i:  [x[0][i], ..., x[n-1][i]]
      -> every position is occupied by at least one vertex.
  (2) For every vertex v:    [x[v][0], ..., x[v][n-1]]
      -> every vertex occurs at least once.
  (3) For every vertex v and i < j:  [-x[v][i], -x[v][j]]
      -> a vertex occurs at most once.
  (4) For every position i and u < v: [-x[u][i], -x[v][i]]
      -> a position holds at most one vertex.
  (5) For every position i (with j = (i+1) mod n) and every non-edge
      {u,v}:  [-x[u][i], -x[v][j]]  and  [-x[v][i], -x[u][j]]
      -> consecutive cycle positions must be joined by an actual edge,
         including the wrap-around from position n-1 back to position 0.

(1)+(2)+(3) already force a bijection between vertices and positions;
(4) is redundant but harmless.  (5) then forces the resulting cyclic
order to be a Hamiltonian cycle.  Conversely any Hamiltonian cycle gives
a satisfying assignment by placing its vertices in order.

The formula has O(n^2) variables and O(n^3) clauses, so the reduction is
polynomial time.  No solver is invoked here.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2: no simple cycle can exist -> unsatisfiable CNF.
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}

    def var(v, i):
        return v * n + i + 1

    clauses = []

    # (1) each position has at least one vertex
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # (2) each vertex appears at least once
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])

    # (3) each vertex appears at most once
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # (4) each position holds at most one vertex
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # (5) consecutive positions must be connected by an edge
    edge_set = set()
    for u, v in edges:
        edge_set.add(frozenset((u, v)))

    for i in range(n):
        j = (i + 1) % n
        for u in range(n):
            for v in range(u + 1, n):
                if frozenset((u, v)) not in edge_set:
                    clauses.append([-var(u, i), -var(v, j)])
                    clauses.append([-var(v, i), -var(u, j)])

    return {"num_vars": n * n, "clauses": clauses}
