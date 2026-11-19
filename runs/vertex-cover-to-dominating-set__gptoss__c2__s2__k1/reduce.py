"""Reduction from Vertex Cover to Dominating Set.

The source problem (VertexCover) instance format is:
    {"n": n, "edges": [[u, v], ...], "k": k}
where vertices are 0..n-1.

The target problem (DominatingSet) uses the same format.

Construction:
For each edge (u, v) of the original graph we introduce a new vertex w
that is adjacent exactly to u and v.  Formally, if the original graph has
`n` vertices and `m` edges, the reduced graph has `n + m` vertices.  The
edge set consists of the original edges (they are not needed for the
correctness of the reduction, but keeping them does not hurt) plus, for
each original edge i = (u, v), the two edges (u, n+i) and (v, n+i).

Correctness sketch:
* If the original graph has a vertex cover C of size ≤ k, then C itself
  dominates the new graph: every original vertex is either in C or has a
  neighbor in C (because each incident edge is covered), and each new
  vertex w is adjacent to an endpoint that lies in C.  Hence the same set
  C is a dominating set of size ≤ k.
* Conversely, suppose D is a dominating set of the new graph with |D| ≤ k.
  If D contains a newly added vertex w, replace w by one of its two
  neighbours (any endpoint of the original edge).  This replacement does
  not increase the size of D and preserves domination because w is
  adjacent to the chosen endpoint and the endpoint dominates itself.
  Repeating this yields a dominating set D' consisting only of original
  vertices, still of size ≤ k.  For each original edge (u, v), the vertex
  w_{uv} must be dominated, so at least one of u or v belongs to D'.  Thus
  D' is a vertex cover of size ≤ k.

Therefore the instance is a yes‑instance for Vertex Cover iff the
constructed instance is a yes‑instance for Dominating Set, and the
transformation runs in polynomial time.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to a DominatingSet instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "n", "edges", and "k" as described in the
        problem statement.

    Returns
    -------
    dict
        An instance of the DominatingSet problem that is equivalent with
        respect to the yes/no answer.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    m = len(edges)
    # New vertices are indexed from n to n+m-1, one per original edge.
    new_edges: List[List[int]] = []

    # Keep original edges (optional, does not affect correctness).
    new_edges.extend([list(e) for e in edges])

    for idx, (u, v) in enumerate(edges):
        w = n + idx  # index of the new vertex for this edge
        # Connect the new vertex to its two endpoints.
        new_edges.append([u, w])
        new_edges.append([v, w])

    reduced_instance = {
        "n": n + m,
        "edges": new_edges,
        "k": k,
    }
    return reduced_instance

