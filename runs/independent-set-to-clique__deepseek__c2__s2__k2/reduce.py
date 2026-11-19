"""Polynomial-time reduction from Independent Set to Clique.

An independent set in a graph G is exactly a clique in the complement
graph of G.  Therefore the reduction keeps n and k unchanged and replaces
the edge set by its complement on the same vertex set.

The construction runs in O(n^2) time, which is polynomial in the input
size (the input lists at most O(n^2) edges).
"""


def reduce(instance):
    """Reduce an IndependentSet instance to a Clique instance.

    Input : {"n": n, "edges": [[u, v], ...], "k": k}
    Output: {"n": n, "edges": [[u, v], ...], "k": k}

    where the output edges are all unordered pairs {u, v} (u < v) that are
    NOT edges of the input graph.  A set S of vertices is independent in the
    input graph iff S is a clique in the complement graph, so the answer is
    preserved for every k (including the k <= 0 and k > n edge cases).
    """
    n = instance["n"]
    k = instance["k"]

    # Normalise the input edges into a set of unordered pairs {u, v}.
    present = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        present.add((u, v))

    # Build the complement: every pair u < v not already an edge.
    complement = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement.append([u, v])

    return {"n": n, "edges": complement, "k": k}
