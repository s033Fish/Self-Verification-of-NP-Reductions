"""Reduction from Vertex Cover to Dominating Set.

Given a Vertex Cover instance (graph G = (V, E) and integer k), we construct a
graph G' for Dominating Set as follows:

* Keep the original vertices V.
* For each edge e = {u, v} in E, introduce a new vertex w_e and add edges
  (u, w_e) and (v, w_e).  These are often called *edge vertices*.
* Add one additional *universal* vertex x that is adjacent to every original
  vertex in V (but not to the edge vertices).

The parameter for the Dominating Set instance is k' = k + 1 (the extra 1
accounts for the universal vertex, which will always be part of any minimum
dominating set).

Correctness sketch:
If C ⊆ V is a vertex cover of size ≤ k in G, then C ∪ {x} dominates all
vertices of G': every original vertex is either in C or adjacent to x; each
edge vertex w_e is adjacent to u or v, and at least one of these is in C.
Thus we obtain a dominating set of size ≤ k+1.
Conversely, let D be a dominating set of G' of size ≤ k+1. Since x dominates
all original vertices, we can assume x ∈ D (otherwise we could replace any
vertex that dominates x by x without increasing the size). Removing x from D
leaves a set D' ⊆ V of size ≤ k that dominates all edge vertices. For each
edge vertex w_e, domination requires that at least one endpoint of e lies in
D', so D' is a vertex cover of G.
Hence G has a vertex cover of size ≤ k iff G' has a dominating set of size ≤ k+1.
"""

def reduce(instance):
    """Reduce a VertexCover instance to a DominatingSet instance.

    Parameters
    ----------
    instance: dict
        Dictionary with keys "n", "edges", and "k" describing the VertexCover
        instance.

    Returns
    -------
    dict
        Corresponding DominatingSet instance.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Start with the original edges (they do not hurt correctness to keep).
    new_edges = list(edges)

    # Add an edge vertex for each original edge and connect it to its endpoints.
    for idx, (u, v) in enumerate(edges):
        edge_vertex = n + idx  # unique identifier for this edge vertex
        new_edges.append([u, edge_vertex])
        new_edges.append([v, edge_vertex])

    # Add a universal vertex adjacent to all original vertices.
    universal = n + len(edges)
    for v in range(n):
        new_edges.append([universal, v])

    new_n = n + len(edges) + 1  # original vertices + edge vertices + universal
    new_k = k + 1                # we need the universal vertex in any solution

    return {"n": new_n, "edges": new_edges, "k": new_k}

if __name__ == "__main__":
    # Example usage (not required for the reduction)
    sample = {"n": 3, "edges": [[0, 1], [1, 2]], "k": 1}
    print(reduce(sample))
