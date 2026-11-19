"""Reduction from 3-Coloring to Independent Set.

The source problem (ThreeColoring) instance format is:
    {"n": n, "edges": [[u, v], ...]}
where vertices are numbered 0..n-1.

The target problem (IndependentSet) instance format is:
    {"n": n', "edges": [[u, v], ...], "k": k}
where we ask for an independent set of size at least k.

Standard polynomial‑time many‑one reduction:
    * For each vertex v in the original graph create three vertices
      (v,0), (v,1), (v,2) representing the choice of colour 0,1,2.
    * Add a triangle among these three vertices so that at most one of
      them can be chosen in an independent set.
    * For each original edge (u,v) and each colour c, add an edge
      between (u,c) and (v,c). This forbids adjacent original vertices
      from receiving the same colour.
    * Set k = n (the number of original vertices). An independent set
      of size n corresponds exactly to a proper 3‑colouring of the
      original graph.

The reduction runs in O(|V|+|E|) time and produces a graph with 3n
vertices and at most 3n + 3|E| edges, which is polynomial.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeColoring instance to an IndependentSet instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"`` (int) and ``"edges"`` (list of
        two‑element lists) describing the input graph.

    Returns
    -------
    dict
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` suitable
        for the IndependentSet problem. The answer to the returned
        instance is *yes* iff the answer to the original instance is
        *yes*.
    """
    n: int = instance.get("n", 0)
    original_edges: List[List[int]] = instance.get("edges", [])

    # New graph will have 3 copies of each vertex.
    new_n = 3 * n
    new_edges: List[List[int]] = []

    # Helper to map (v, colour) -> new vertex index.
    def idx(v: int, colour: int) -> int:
        return 3 * v + colour

    # 1. Add a triangle for each original vertex to enforce at most one colour.
    for v in range(n):
        a = idx(v, 0)
        b = idx(v, 1)
        c = idx(v, 2)
        new_edges.append([a, b])
        new_edges.append([a, c])
        new_edges.append([b, c])

    # 2. For each original edge, forbid same colour on both ends.
    for u, v in original_edges:
        for colour in range(3):
            new_edges.append([idx(u, colour), idx(v, colour)])

    # Target independent set size k should be exactly n.
    k = n

    return {"n": new_n, "edges": new_edges, "k": k}

