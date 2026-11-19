"""Polynomial-time reduction from Vertex Cover to Set Cover.

Given a Vertex Cover instance {"n": n, "edges": [[u, v], ...], "k": k},
build a Set Cover instance as follows:

  * Universe: one element per edge.  Edge i (0-indexed in the input list)
    becomes element i, so universe_size = number of edges.
  * For every vertex v in 0..n-1, create the set of all edge-elements
    incident to v.
  * Keep k unchanged.

A set of vertices covers every edge iff the corresponding collection of
vertex-sets covers every edge-element.  Hence the graph has a vertex cover
of size at most k iff the constructed set system has a set cover of size at
most k.  The construction is linear in the size of the input (O(n + m)
sets/elements, O(n*m) total listed incidences in the worst case), so it runs
in polynomial time.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Map each edge to a universe element (its index).
    universe_size = len(edges)

    # incident[v] = list of edge indices incident to vertex v.
    incident = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        incident[u].append(i)
        incident[v].append(i)

    # One set per vertex: all edges it covers.
    sets = [list(edge_indices) for edge_indices in incident]

    return {"universe_size": universe_size, "sets": sets, "k": k}
