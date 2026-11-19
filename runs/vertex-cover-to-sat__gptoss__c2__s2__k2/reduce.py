"""Reduction from Vertex Cover to SAT.

The reduction encodes the existence of a vertex cover of size at most k.
We achieve an "at most k" condition by adding k isolated dummy vertices to the
graph. Any cover of size ≤k can be extended with some of these dummy vertices
to a cover of size exactly k, and any exact‑k cover of the augmented graph
yields a ≤k cover of the original graph after discarding dummy vertices.

Variables:
    x_{i,j}  (i = 0..n_aug-1, j = 0..k-1)
    means "vertex i occupies position j in the chosen cover".
The encoding forces exactly one vertex per position and at most one position
per vertex, thus selecting exactly k distinct vertices.
Edge constraints only involve the original vertices; dummy vertices have
no incident edges, so they never affect satisfaction of those clauses.
"""

def reduce(instance):
    """Convert a VertexCover instance to a SAT instance.

    Parameters
    ----------
    instance: dict with keys 'n', 'edges', 'k'
        * n – number of vertices (0..n-1)
        * edges – list of [u, v] undirected edges
        * k – size bound for the vertex cover (may be any integer)

    Returns
    -------
    dict with keys 'num_vars', 'clauses' suitable for the SAT problem.
    """
    n = instance.get('n')
    edges = instance.get('edges', [])
    k = instance.get('k')

    # ---------- Edge cases handling ----------
    # k < 0 -> impossible
    if k < 0:
        return {"num_vars": 1, "clauses": [[]]}  # unsatisfiable (empty clause)

    # No edges: always satisfiable for any k >= 0
    if not edges:
        # Trivially satisfiable formula (no constraints)
        return {"num_vars": 1, "clauses": []}

    # k >= n -> always yes (take all vertices)
    if k >= n:
        return {"num_vars": 1, "clauses": []}

    # ---------- General case ----------
    # Augment graph with k isolated dummy vertices (indices n .. n+k-1)
    n_aug = n + k

    # Number of SAT variables: one for each (vertex, position) pair
    num_vars = n_aug * k
    def var(i, j):
        """Return SAT variable index for vertex i at position j (0‑based).
        Variables are 1‑based as required by the SAT format.
        """
        return i * k + j + 1

    clauses = []

    # 1. Each position j must be occupied by at least one vertex.
    for j in range(k):
        clause = [var(i, j) for i in range(n_aug)]
        clauses.append(clause)

    # 2. A vertex cannot occupy two different positions (at most once).
    for i in range(n_aug):
        for j in range(k):
            for l in range(j + 1, k):
                clauses.append([-var(i, j), -var(i, l)])

    # 3. A position cannot be occupied by two different vertices (at most one).
    for j in range(k):
        for i in range(n_aug):
            for l in range(i + 1, n_aug):
                clauses.append([-var(i, j), -var(l, j)])

    # 4. Edge covering constraints: for each original edge (u, v), at least one
    #    endpoint must be selected in some position.
    for (u, v) in edges:
        clause = []
        for j in range(k):
            clause.append(var(u, j))
            clause.append(var(v, j))
        clauses.append(clause)

    return {"num_vars": num_vars, "clauses": clauses}

