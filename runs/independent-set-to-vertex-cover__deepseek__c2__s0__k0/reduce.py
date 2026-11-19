"""Polynomial-time reduction from Independent Set to Vertex Cover.

An instance of Independent Set is a graph G = (V, E) with |V| = n and an
integer k; it is a yes-instance iff G has an independent set of size at
least k.

A set S is independent in G iff its complement V \ S is a vertex cover:
every edge has at least one endpoint outside S (otherwise both endpoints
would lie in S, contradicting independence).  Consequently G has an
independent set of size at least k iff G has a vertex cover of size at
most n - k.

The reduction therefore keeps n and the edge list unchanged and maps the
threshold k to n - k.  It is clearly computable in polynomial time (indeed
linear time in the size of the instance) and does not solve either problem.
"""


def reduce(instance):
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Input format:  {"n": n, "edges": [[u, v], ...], "k": k}
    Output format: {"n": n, "edges": [[u, v], ...], "k": n - k}
    """
    n = instance["n"]
    edges = [[u, v] for u, v in instance["edges"]]
    return {"n": n, "edges": edges, "k": n - instance["k"]}
