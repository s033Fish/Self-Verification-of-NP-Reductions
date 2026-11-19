"""Reduction from 3-Coloring to Independent Set.

The source problem (ThreeColoring) expects an instance of the form::

    {"n": n, "edges": [[u, v], ...]}

where ``n`` is the number of vertices (labelled ``0`` … ``n-1``) and each
edge is an undirected pair of distinct vertices.

The target problem (IndependentSet) expects an instance of the form::

    {"n": n2, "edges": [[u, v], ...], "k": k}

where ``k`` is the size requirement for the independent set.

The classic polynomial‑time reduction creates three “colour‑vertices” for
each original vertex.  Vertices representing the same original vertex are
made pairwise adjacent, forcing any independent set to contain at most one
of them.  For each original edge ``(u, v)`` we also connect the colour‑
vertices that share the same colour, prohibiting adjacent original
vertices from receiving the same colour.

With this construction an independent set of size exactly ``n`` exists
iff the original graph is 3‑colourable.  Therefore we set ``k = n`` and
``n2 = 3 * n``.

The reduction runs in O(|V| + |E|) time and uses only basic Python data
structures.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeColoring instance to an IndependentSet instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (int) and ``"edges"`` (list of
        two‑element lists).  The format follows the description in the
        problem statement.

    Returns
    -------
    dict
        An IndependentSet instance ``{"n": n2, "edges": edges2, "k": k}``
        such that the answer to the IndependentSet instance is *yes* iff
        the answer to the original ThreeColoring instance is *yes*.
    """

    n: int = instance["n"]
    original_edges: List[List[int]] = instance.get("edges", [])

    # Number of vertices in the new graph: three copies per original vertex.
    n2: int = 3 * n
    k: int = n  # we ask for an independent set of size exactly n

    # Helper to map (vertex, colour) -> new vertex id.
    def vid(v: int, colour: int) -> int:
        return v * 3 + colour

    new_edges: List[List[int]] = []

    # 1. Make each triple of colour‑vertices a triangle (mutual adjacency).
    for v in range(n):
        a = vid(v, 0)
        b = vid(v, 1)
        c = vid(v, 2)
        new_edges.append([a, b])
        new_edges.append([a, c])
        new_edges.append([b, c])

    # 2. For each original edge, forbid the same colour on both ends.
    for u, v in original_edges:
        # Ensure the edge is stored with u < v (not strictly required but
        # keeps the output tidy).
        if u == v:
            # The source specification guarantees u != v, but we guard
            # against malformed input just in case.
            continue
        for colour in range(3):
            new_edges.append([vid(u, colour), vid(v, colour)])

    # The format for IndependentSet expects a list of edges where each edge
    # appears only once.  The construction above never adds duplicate edges,
    # but we can defensively remove any potential duplicates by using a set.
    # This also normalises the order of the two vertices in each edge.
    edge_set = {tuple(sorted(e)) for e in new_edges}
    final_edges = [list(e) for e in edge_set]

    return {"n": n2, "edges": final_edges, "k": k}

