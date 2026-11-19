"""Polynomial-time reduction from Hamiltonian Cycle (undirected) to SAT.

Encoding
--------
For a graph on n vertices we introduce boolean variable x_{v,i} for every
vertex v in 0..n-1 and every position i in 0..n-1.  Intuitively x_{v,i} is
true when vertex v is the i-th vertex of the cycle.

Variable number: var(v, i) = v * n + i + 1, so variables are 1..n*n.

Clauses:
  * For every vertex v:  [x_{v,0}, ..., x_{v,n-1}]
        every vertex occurs somewhere in the cycle.
  * For every position i: [x_{0,i}, ..., x_{n-1,i}]
        every position is occupied by some vertex.
  * For every vertex v and positions i < j: [-x_{v,i}, -x_{v,j}]
        a vertex occurs at most once.
  * For every position i and vertices u < v: [-x_{u,i}, -x_{v,i}]
        a position holds at most one vertex.
  * For every position i and every ordered pair (u, v), u != v, such that
    {u, v} is NOT an edge: [-x_{u,i}, -x_{v,(i+1) mod n}]
        consecutive positions must be joined by an edge (including the wrap
        from position n-1 back to position 0).

Together the first four groups force a bijection between vertices and
positions, i.e. a cyclic ordering of all vertices; the last group forces
each consecutive pair (cyclically) to be an edge.  Hence the formula is
satisfiable exactly when the graph has a Hamiltonian cycle.

Edge cases: a simple graph with n <= 2 can never contain a cycle, so for
those inputs we return the unsatisfiable formula {"num_vars": 0,
"clauses": [[]]} (an empty clause is never satisfiable).  This also covers
n = 0 and n = 1 (where no edge can exist at all).

The construction uses O(n^2) variables and O(n^3) clauses, hence runs in
polynomial time.  No brute-force solver is invoked.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2: no Hamiltonian cycle exists.  Return an unsatisfiable formula.
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}

    def var(v, i):
        # vertex v (0..n-1) at position i (0..n-1) -> variable 1..n*n
        return v * n + i + 1

    # Set of undirected edges as frozensets for O(1) membership tests.
    edge_set = set()
    for u, v in edges:
        edge_set.add(frozenset((u, v)))

    clauses = []

    # 1. Every vertex occurs at least once.
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])

    # 2. Every position is occupied by at least one vertex.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # 3. Every vertex occurs at most once.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # 4. Every position holds at most one vertex.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # 5. Consecutive positions (cyclically) must be connected by an edge.
    for i in range(n):
        j = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if frozenset((u, v)) not in edge_set:
                    clauses.append([-var(u, i), -var(v, j)])

    return {"num_vars": n * n, "clauses": clauses}
