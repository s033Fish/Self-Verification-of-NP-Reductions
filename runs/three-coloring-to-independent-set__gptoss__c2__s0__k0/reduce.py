"""Reduction from Three-Coloring to Independent Set.

The source problem is defined in ``problems.py`` as ``ThreeColoring`` with
instance format ``{"n": n, "edges": [[u, v], ...]}``.  The target problem is
``IndependentSet`` with instance format ``{"n": n, "edges": [[u, v], ...],
"k": k}``.

The classic polynomial‑time reduction creates, for each vertex *v* of the
original graph, three copies representing the three possible colours.  We
connect the three copies of the same vertex to forbid selecting more than one
colour for that vertex.  For every original edge *(u, v)* we connect the copies
that share the same colour, because two adjacent vertices cannot be assigned
the same colour in a proper 3‑colouring.

Formally, let the original vertex set be ``V = {0,…,n-1}``.  The new vertex set
is ``V' = {(v, c) | v in V, c in {0,1,2}}``.  We index these vertices linearly
as ``v' = v*3 + c``.  The edge set consists of:

* For each original vertex ``v`` – a triangle between ``(v,0)``, ``(v,1)``
  and ``(v,2)``.
* For each original edge ``[u, v]`` and each colour ``c`` – an edge between
  ``(u,c)`` and ``(v,c)``.

The constructed instance asks for an independent set of size ``k = n``.  An
independent set of that size selects exactly one colour vertex for each
original vertex, which corresponds to a proper 3‑colouring.  Conversely, a
proper 3‑colouring yields such an independent set.  Hence the reduction is
correct.

The implementation below follows this description and runs in O(|V| +
|E|) time, which is polynomial.
"""

from __future__ import annotations

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeColoring instance to an IndependentSet instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"`` (int) and ``"edges"`` (list of
        two‑element lists) describing an undirected simple graph.

    Returns
    -------
    dict
        An IndependentSet instance with keys ``"n"``, ``"edges"`` and ``"k"``.
        The answer to the returned instance is *yes* iff the answer to the
        original instance is *yes*.
    """

    n: int = instance["n"]
    orig_edges: List[List[int]] = instance.get("edges", [])

    # New graph will have 3 copies per original vertex.
    new_n = n * 3
    new_edges: List[List[int]] = []

    # Helper to map (v, colour) -> new vertex index.
    def idx(v: int, colour: int) -> int:
        return v * 3 + colour

    # 1. Add triangles for each original vertex to enforce at most one colour.
    for v in range(n):
        a = idx(v, 0)
        b = idx(v, 1)
        c = idx(v, 2)
        new_edges.append([a, b])
        new_edges.append([a, c])
        new_edges.append([b, c])

    # 2. For each original edge, forbid equal colours on its endpoints.
    for u, v in orig_edges:
        for colour in range(3):
            new_u = idx(u, colour)
            new_v = idx(v, colour)
            new_edges.append([new_u, new_v])

    # The target asks for an independent set of size exactly n (one per vertex).
    target_instance = {
        "n": new_n,
        "edges": new_edges,
        "k": n,
    }
    return target_instance

