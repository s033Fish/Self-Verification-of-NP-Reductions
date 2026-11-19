"""Reduction from Vertex Cover to Dominating Set.

The source problem (VertexCover) instance format is a dictionary with keys
``n`` (number of vertices), ``edges`` (list of undirected edges as ``[u, v]``)
and ``k`` (size bound).  Vertices are numbered ``0 .. n-1``.

The target problem (DominatingSet) uses the same format.

Reduction construction
----------------------
Given a Vertex Cover instance ``G = (V, E)`` with ``|V| = n`` we build a
graph ``G' = (V', E')`` as follows:

* For each original vertex ``v`` we keep it unchanged.
* For each original edge ``e = {u, v}`` we introduce a fresh vertex ``w_e``.
* The edge set of ``G'`` consists of:
    - all original edges ``(u, v)`` (so the original adjacency is retained),
    - the two edges ``(u, w_e)`` and ``(v, w_e)`` connecting the new vertex to
      the endpoints of the original edge.

The new graph has ``n' = n + |E|`` vertices.  The parameter ``k`` is left
unchanged.

Correctness sketch
-------------------
*If* ``G`` has a vertex cover ``C`` of size at most ``k``, then ``C`` is also a
 dominating set of ``G'``: every original vertex not in ``C`` is adjacent (via an
 original edge) to a vertex in ``C`` because the incident edge is covered.
 Each new vertex ``w_e`` is adjacent to the two endpoints of ``e`` and at least
 one of them belongs to ``C`` (since ``C`` covers ``e``).  Hence ``C`` dominates
 all vertices of ``G'``.

*Conversely*, let ``D`` be a dominating set of ``G'`` with ``|D| ≤ k``.
For any edge ``e = {u, v}`` the vertex ``w_e`` must be dominated, so at least
 one of ``u, v, w_e`` is in ``D``.  If ``w_e ∈ D`` we can replace it by either
 ``u`` or ``v`` (both still dominate ``w_e``) without increasing the size of the
 set.  Repeating this for all edges yields a dominating set consisting only of
 original vertices.  Such a set necessarily covers every edge (otherwise the
 corresponding ``w_e`` would be undominated), thus it is a vertex cover of ``G``
 of size at most ``k``.

Therefore the instance ``(G, k)`` is a YES‑instance of Vertex Cover iff the
 constructed instance ``(G', k)`` is a YES‑instance of Dominating Set.

The transformation runs in time linear in the size of the input graph, i.e.
 polynomial time.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a Vertex Cover instance to a Dominating Set instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``n``, ``edges`` and ``k`` representing a
        Vertex Cover instance.

    Returns
    -------
    dict
        A dictionary in the same format representing a Dominating Set
        instance that is equivalent to the input.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    m = len(edges)
    # New vertices are indexed from n to n+m-1, one for each original edge.
    new_n = n + m
    new_edges: List[List[int]] = []

    # Keep original edges.
    for u, v in edges:
        new_edges.append([u, v])

    # Add gadget edges for each original edge.
    for idx, (u, v) in enumerate(edges):
        w = n + idx  # new vertex for this edge
        new_edges.append([u, w])
        new_edges.append([v, w])

    return {"n": new_n, "edges": new_edges, "k": k}

