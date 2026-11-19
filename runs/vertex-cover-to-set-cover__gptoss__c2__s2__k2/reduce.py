#!/usr/bin/env python3
"""Reduction from Vertex Cover to Set Cover.

Given an instance of Vertex Cover:
    {"n": n, "edges": [[u, v], ...], "k": k}
we produce an equivalent Set Cover instance:
    {"universe_size": m, "sets": [[...], ...], "k": k}
where each edge becomes an element of the universe, and for each vertex we
create a set containing all edges incident to that vertex.
"""

def reduce(instance):
    """Reduce a Vertex Cover instance to a Set Cover instance.

    Parameters
    ----------
    instance: dict
        Vertex Cover instance with keys "n", "edges", and "k".

    Returns
    -------
    dict
        Set Cover instance with keys "universe_size", "sets", and "k".
    """
    n = instance.get("n")
    edges = instance.get("edges", [])
    k = instance.get("k")

    m = len(edges)  # number of edges = universe size
    # Prepare a list for each vertex to collect incident edge indices
    vertex_sets = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        # assume vertices are valid 0..n-1 as per problem statement
        vertex_sets[u].append(idx)
        vertex_sets[v].append(idx)

    # Convert to the required format (list of lists of ints)
    sets = [list(s) for s in vertex_sets]

    return {"universe_size": m, "sets": sets, "k": k}

# If this file is executed directly, perform a simple sanity test.
if __name__ == "__main__":
    # Example: triangle graph, n=3, edges=[[0,1],[1,2],[0,2]], k=2
    example = {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2}
    print(reduce(example))
