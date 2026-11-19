"""Reduction from Vertex Cover to Dominating Set.

The source problem (VertexCover) expects instances of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

where ``n`` is the number of vertices labelled ``0..n-1`` and ``edges`` is a
list of undirected edges.  The target problem (DominatingSet) uses the same
graph representation but asks for a dominating set of size at most ``k``.

We implement the classic polynomial‑time reduction that *subdivides* every
edge of the original graph.  For each edge ``(u, v)`` we introduce a new
vertex ``w`` and connect it only to ``u`` and ``v``.  The resulting graph
contains ``|V| + |E|`` vertices and ``2·|E|`` edges.  The parameter ``k`` is
kept unchanged.

Why does this work?
--------------------
*If* the original graph has a vertex cover ``C`` of size ``≤ k``, then ``C``
 dominates the subdivided graph: every new vertex ``w`` is adjacent to at
least one endpoint of its original edge, which lies in ``C``; all original
vertices are either in ``C`` or adjacent to a vertex of ``C`` via an original
edge.  Hence ``C`` is a dominating set of size ``≤ k``.

Conversely, let ``D`` be a dominating set of the subdivided graph of size
``≤ k``.  If ``D`` contains a subdivision vertex ``w``, we can replace ``w``
by any of its two neighbours without increasing the set size while still
dominating everything (``w`` only dominates its two neighbours).  Repeating
this replacement yields a dominating set consisting solely of original
vertices.  Such a set must intersect each original edge, otherwise the
corresponding subdivision vertex would be undominated.  Therefore the set is
indeed a vertex cover of the original graph of size ``≤ k``.

Isolated vertices pose no problem: they never appear in any edge, so they are
simply omitted from the constructed instance.  An empty edge set maps to an
empty graph, which is a yes‑instance for both problems (the dominating set
instance has ``n = 0`` and is trivially dominated).

The implementation below follows this construction exactly and runs in
polynomial time.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to a DominatingSet instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` following the
        specification of VertexCover.

    Returns
    -------
    dict
        An instance suitable for DominatingSet with the same ``k``.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Determine which original vertices actually appear in an edge.
    used_vertices = set()
    for u, v in edges:
        used_vertices.add(u)
        used_vertices.add(v)

    # Mapping from old vertex id to new contiguous ids (0..v_cnt-1).
    old_to_new: Dict[int, int] = {}
    for new_id, old_id in enumerate(sorted(used_vertices)):
        old_to_new[old_id] = new_id
    v_cnt = len(old_to_new)  # number of original vertices that remain

    # Build the edge list of the subdivided graph.
    new_edges: List[List[int]] = []
    # Index for the subdivision vertices starts after the original ones.
    subdiv_index = v_cnt
    for u, v in edges:
        nu = old_to_new[u]
        nv = old_to_new[v]
        w = subdiv_index
        subdiv_index += 1
        # Connect the subdivision vertex to its two endpoints.
        new_edges.append([nu, w])
        new_edges.append([nv, w])

    total_vertices = v_cnt + len(edges)  # one subdivision vertex per original edge

    return {"n": total_vertices, "edges": new_edges, "k": k}

