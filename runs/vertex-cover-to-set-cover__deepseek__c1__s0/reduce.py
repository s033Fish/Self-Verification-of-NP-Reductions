"""Polynomial-time reduction from Vertex Cover to Set Cover.

Source instance (Vertex Cover):
    {"n": n, "edges": [[u, v], ...], "k": k}

Target instance (Set Cover):
    {"universe_size": u, "sets": [[element, ...], ...], "k": k}

Reduction:
    * The universe is the set of edges of the graph (each edge is an element).
    * For every vertex v in 0..n-1 create one set consisting of all edges
      incident to v.
    * Keep k unchanged.

Correctness:
    A vertex cover C of size c selects the c sets of its vertices, and every
    edge is incident to some vertex of C, so those sets cover the universe.
    Conversely, any collection of c sets covering all edges corresponds to a
    set of at most c vertices that touches every edge, i.e. a vertex cover of
    size at most c.  Hence a cover of size at most k exists iff a vertex cover
    of size at most k exists.

    Edge cases match as well:
      * k < 0: both problems answer no.
      * No edges: the universe is empty, so the target is yes for every
        k >= 0 (choosing no sets), matching the source.
      * k >= n: all n vertex sets cover the universe whenever there are edges,
        and the empty universe is trivially covered, so the target is yes,
        matching the source.

The construction uses O(n + m) sets/elements and runs in O(n + m) time.
"""

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Vertex Cover instance to an equivalent Set Cover instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Element e (0 <= e < len(edges)) represents the undirected edge edges[e].
    universe_size = len(edges)

    # sets[v] contains every edge incident to vertex v.
    sets: list[list[int]] = [[] for _ in range(n)]
    for e, (u, v) in enumerate(edges):
        sets[u].append(e)
        sets[v].append(e)

    return {"universe_size": universe_size, "sets": sets, "k": k}
