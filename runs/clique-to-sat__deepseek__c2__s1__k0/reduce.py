"""Polynomial-time reduction from Clique to SAT.

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
SAT    instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction (for 1 <= k <= n):
  Variable x_{i,v} (1-indexed as i*n + v + 1) means "the i-th chosen
  clique vertex is v", for positions i = 0..k-1 and vertices v = 0..n-1.

  Clauses:
    * for each position i: [x_{i,0}, ..., x_{i,n-1}]
        -> every position gets at least one vertex.
    * for each position i and each pair u < v: [-x_{i,u}, -x_{i,v}]
        -> each position gets at most one vertex.
    * for each pair of positions i < j and each ordered pair of vertices
      (u, v) that are NOT connected by an edge (including u == v):
      [-x_{i,u}, -x_{j,v}]
        -> vertices chosen in different positions must be distinct and
           adjacent, so the selected k vertices form a clique.

  A satisfying assignment picks k pairwise-adjacent vertices, i.e. a clique
  of size k.  A clique of size >= k yields one by choosing any k of its
  vertices.  Hence the formula is satisfiable iff Clique is yes.

Edge cases:
  * k <= 0: Clique is always yes -> return an empty (trivially SAT) formula.
  * k > n:  Clique is always no  -> return a formula with an empty clause.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k <= 0: always yes; the empty CNF is satisfiable.
    if k <= 0:
        return {"num_vars": 0, "clauses": []}

    # k > n: cannot have a clique of at least k vertices; empty clause is UNSAT.
    if k > n:
        return {"num_vars": 0, "clauses": [[]]}

    # Now 1 <= k <= n.
    num_vars = k * n

    def var(i, v):
        # position i in 0..k-1, vertex v in 0..n-1 -> variable in 1..k*n
        return i * n + v + 1

    # Adjacency set of undirected edges.
    adjacent = set()
    for u, v in edges:
        adjacent.add((u, v))
        adjacent.add((v, u))

    clauses = []

    # At least one vertex per position.
    for i in range(k):
        clauses.append([var(i, v) for v in range(n)])

    # At most one vertex per position.
    for i in range(k):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(i, u), -var(i, v)])

    # Chosen vertices in different positions must be distinct and adjacent.
    for i in range(k):
        for j in range(i + 1, k):
            for u in range(n):
                for v in range(n):
                    if u == v or (u, v) not in adjacent:
                        clauses.append([-var(i, u), -var(j, v)])

    return {"num_vars": num_vars, "clauses": clauses}
