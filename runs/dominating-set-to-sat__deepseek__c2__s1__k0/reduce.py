"""Polynomial-time reduction from Dominating Set to SAT.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
For every vertex v in 0..n-1 we introduce a Boolean variable x_v (encoded as
literal v+1) meaning "v belongs to the dominating set D".

1. Domination: for each vertex u we add the clause

       (x_u OR x_{v1} OR ... OR x_{vd})

   where v1..vd are the neighbours of u.  This says every vertex is either in
   D or adjacent to a vertex of D.

2. Cardinality "at most k": we use the standard sequential-counter encoding
   (Sinz).  Auxiliary variable s(i, j) means "at least j of x_1..x_i are
   true", for 1 <= i <= n and 1 <= j <= k.  The clauses are

       (~x_i OR s(i,1))                         1 <= i <= n
       (~s(i-1,1) OR s(i,1))                    2 <= i <= n
       (~x_i OR ~s(i-1,j-1) OR s(i,j))          2 <= i <= n, 2 <= j <= k
       (~s(i-1,j) OR s(i,j))                    2 <= i <= n, 2 <= j <= k
       (~x_i OR ~s(i-1,k))                      k+1 <= i <= n

   The last group forbids selecting a (k+1)-st vertex.

Edge cases
----------
* k < 0: the answer is always no; return the unsatisfiable formula [[]].
* k >= n: the answer is always yes; return the satisfiable empty formula.
* k = 0 (and n > 0): no vertex may be selected; add unit clauses ~x_v.
* n = 0: covered by k >= n (for k >= 0) and k < 0 respectively.

The number of variables is n + n*k and the number of clauses is
O(n + n*k + |E|), so the reduction is polynomial in the input size.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0: no dominating set of size at most k exists.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # All n vertices form a dominating set, so any k >= n is a yes instance.
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # From here on 0 <= k < n and n > 0.

    # Build adjacency lists.
    adjacency = [set() for _ in range(n)]
    for edge in edges:
        u, v = edge[0], edge[1]
        adjacency[u].add(v)
        adjacency[v].add(u)

    clauses = []

    # 1. Every vertex must be dominated.
    for u in range(n):
        clause = [u + 1]  # x_u
        for v in adjacency[u]:
            clause.append(v + 1)  # x_v
        clauses.append(clause)

    # 2. At most k selected vertices.
    if k == 0:
        for v in range(n):
            clauses.append([-(v + 1)])
        return {"num_vars": n, "clauses": clauses}

    # Auxiliary variables s(i, j), 1 <= i <= n, 1 <= j <= k.
    num_vars = n + n * k

    def s(i, j):
        return n + (i - 1) * k + j

    for i in range(1, n + 1):
        clauses.append([-i, s(i, 1)])

    for i in range(2, n + 1):
        clauses.append([-s(i - 1, 1), s(i, 1)])

    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([-i, -s(i - 1, j - 1), s(i, j)])
            clauses.append([-s(i - 1, j), s(i, j)])

    for i in range(k + 1, n + 1):
        clauses.append([-i, -s(i - 1, k)])

    return {"num_vars": num_vars, "clauses": clauses}
