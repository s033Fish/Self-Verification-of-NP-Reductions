"""Reduction from 3-Coloring to Independent Set.

The source problem is ``ThreeColoring`` with instances of the form:
    {"n": n, "edges": [[u, v], ...]}
where vertices are 0‑based and the graph is undirected.

The target problem is ``IndependentSet`` with instances of the form:
    {"n": n', "edges": [[u, v], ...], "k": k}
where ``k`` is the required size of the independent set.

We use the classic polynomial‑time reduction:

* For each original vertex ``v`` we create three copies ``(v,0)``,
  ``(v,1)`` and ``(v,2)`` representing the three possible colours.
* Copies belonging to the same original vertex are made pairwise adjacent
  (forming a triangle). This forces an independent set to contain at most
  one copy of each original vertex.
* For each original edge ``(u, v)`` and for each colour ``c`` we add an edge
  between ``(u,c)`` and ``(v,c)``. This forbids two adjacent vertices from
  receiving the same colour.

With this construction the original graph is 3‑colourable iff the new graph
has an independent set of size exactly ``n`` (one colour‑choice per vertex).

The reduction runs in time O(|V| + |E|) and the output instance respects the
format required by ``problems.py``.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Set


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeColoring instance to an IndependentSet instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (int) and ``"edges"`` (list of
        two‑element lists). The format follows the description in
        ``problems.py`` for the ``ThreeColoring`` problem.

    Returns
    -------
    Dict
        An IndependentSet instance ``{"n": n', "edges": [...], "k": k}``.
        ``n' = 3 * n`` and ``k = n``.
    """

    n: int = instance["n"]
    original_edges: List[List[int]] = instance.get("edges", [])

    # New graph will have 3 * n vertices.
    new_n: int = 3 * n
    k: int = n  # we ask for an independent set of size n.

    # Helper to map (v, colour) -> vertex id in the new graph.
    def vid(v: int, colour: int) -> int:
        return v * 3 + colour  # colour in {0,1,2}

    edge_set: Set[Tuple[int, int]] = set()

    # 1. Add triangle edges for each original vertex.
    for v in range(n):
        a, b, c = vid(v, 0), vid(v, 1), vid(v, 2)
        # Add edges (a,b), (a,c), (b,c)
        edge_set.add(tuple(sorted((a, b))))
        edge_set.add(tuple(sorted((a, c))))
        edge_set.add(tuple(sorted((b, c))))

    # 2. For each original edge, forbid same colour on both ends.
    for u, v in original_edges:
        # Ensure the edge is undirected; the input guarantees u != v.
        for colour in range(3):
            a = vid(u, colour)
            b = vid(v, colour)
            edge_set.add(tuple(sorted((a, b))))

    # Convert edge set to list of [u, v] pairs.
    new_edges: List[List[int]] = [list(e) for e in edge_set]

    return {"n": new_n, "edges": new_edges, "k": k}

