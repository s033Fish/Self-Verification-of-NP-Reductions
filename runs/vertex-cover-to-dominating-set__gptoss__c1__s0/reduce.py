"""Reduction from Vertex Cover to Dominating Set.

The source problem (VertexCover) instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}
The target problem (DominatingSet) uses the same dictionary keys.

We construct a graph G' from the input graph G as follows.

* For every edge (u, v) in G we add a new vertex e_uv that is adjacent to
  u and v.  These vertices force any dominating set to include at least one
  endpoint of the original edge – otherwise the new vertex would be
  undominated.  An optimal dominating set never needs to pick e_uv itself
  because we can replace it with one of its neighbours without increasing the
  set size.  Consequently the part of a minimum dominating set that lies in
  the original vertex set is a vertex cover of G.

* Isolated vertices (vertices of degree 0) cause a mismatch between the two
  problems: a vertex cover can ignore isolated vertices, whereas a dominating
  set must contain each isolated vertex.  To bridge this gap we attach a leaf
  vertex to every isolated vertex.  The leaf can dominate its neighbour, so
  the isolated vertex does not have to be selected directly.  Each such leaf
  contributes exactly one extra vertex to any dominating set.

Let I be the set of isolated vertices in the original instance.  The
transformation creates:
    - n + |E| + |I| vertices,
    - the original edges,
    - for each original edge (u, v) two new edges (u, e_uv) and (v, e_uv),
    - for each isolated vertex v a leaf ℓ_v with edge (v, ℓ_v).

The parameter for the Dominating Set instance is
    k' = k            if k < 0 (preserve the trivial “no” case),
    k' = k + |I|     otherwise.

Correctness sketch:
* (⇒) Suppose G has a vertex cover C of size ≤ k.  Build a dominating set D
  for G' by taking C, and for every isolated vertex v∈I add its leaf ℓ_v.
  All original vertices are either in C or adjacent to a vertex of C, thus
  they dominate the edge‑gadgets.  Each leaf dominates its isolated vertex.
  |D| ≤ k + |I| = k'.
* (⇐) Conversely, let D be a dominating set of G' of size ≤ k'.  For each
  isolated vertex v we may assume D contains the leaf ℓ_v (otherwise we can
  replace v by ℓ_v without increasing the size).  Removing all leaves leaves a
  set C ⊆ V(G) of size ≤ k that dominates every edge‑gadget, which means C
  hits at least one endpoint of every original edge – i.e., C is a vertex
  cover of G.

The construction runs in time polynomial in the size of the input.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to a DominatingSet instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "n", "edges", and "k" as described above.

    Returns
    -------
    dict
        An instance of the Dominating Set problem that is yes‑equivalent to
        the given Vertex Cover instance.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Compute degrees to identify isolated vertices.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    isolated_vertices = [v for v in range(n) if degree[v] == 0]

    m = len(edges)
    new_edges: List[List[int]] = []
    # Preserve original edges (they do not affect the reduction but keeping
    # them does not hurt correctness).
    new_edges.extend([list(e) for e in edges])

    # Edge‑gadgets: for each original edge create a new vertex adjacent to its
    # endpoints.
    for idx, (u, v) in enumerate(edges):
        new_vertex = n + idx  # unique id for the gadget vertex
        new_edges.append([u, new_vertex])
        new_edges.append([v, new_vertex])

    # Leaf gadgets for isolated vertices.
    leaf_start = n + m  # start index for leaf vertices
    for i, v in enumerate(isolated_vertices):
        leaf = leaf_start + i
        new_edges.append([v, leaf])

    new_n = n + m + len(isolated_vertices)
    # Preserve the trivial no‑case when k is negative.
    new_k = k if k < 0 else k + len(isolated_vertices)

    return {"n": new_n, "edges": new_edges, "k": new_k}

