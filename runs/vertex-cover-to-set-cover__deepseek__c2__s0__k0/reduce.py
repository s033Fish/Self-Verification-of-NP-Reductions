"""Polynomial-time reduction from Vertex Cover to Set Cover.

Vertex Cover instance: {"n": n, "edges": [[u, v], ...], "k": k}
Set Cover instance:     {"universe_size": u, "sets": [[element, ...], ...], "k": k}

Reduction: the universe is the set of edges (edge i corresponds to element i).
For every vertex v we create one set containing the indices of all edges
incident to v.  A collection of vertex-sets covers the universe iff the
corresponding vertices touch every edge, i.e. form a vertex cover.  Hence the
minimum set cover size equals the minimum vertex cover size, so the answer is
preserved for the same k.

Edge cases:
  * k < 0: both problems answer no (SetCover.is_yes returns False for k < 0).
  * No edges: universe_size = 0, which is yes for every k >= 0.
  * k >= n: all n vertex-sets together cover every edge, so the target is yes.
  * Vertices with no incident edges simply yield empty sets, which is allowed.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # One set per vertex; sets[v] collects the indices of edges incident to v.
    sets = [[] for _ in range(n)]
    for index, (u, v) in enumerate(edges):
        sets[u].append(index)
        sets[v].append(index)

    return {"universe_size": len(edges), "sets": sets, "k": k}
