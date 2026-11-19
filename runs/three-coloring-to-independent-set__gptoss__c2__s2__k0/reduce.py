"""Reduction from 3-Coloring to Independent Set.

The source problem (ThreeColoring) expects an instance of the form:
    {"n": n, "edges": [[u, v], ...]}
where vertices are numbered 0..n-1.

The target problem (IndependentSet) expects an instance of the form:
    {"n": N, "edges": [[u, v], ...], "k": k}
and asks whether the graph contains an independent set of size at least k.

Standard polynomial‑time reduction:
    * For each original vertex v we create three vertices (v,0), (v,1), (v,2)
      representing the choice of colour 0, 1 or 2.
    * We add a triangle among these three copies so that at most one of them
      can be chosen in an independent set.
    * For each original edge (u, v) we add edges between the copies of the
      same colour: (u,i) – (v,i) for i = 0,1,2. This forbids adjacent vertices
      from receiving the same colour.
    * We set k = original number of vertices n.  An independent set of size n
      corresponds exactly to a proper 3‑colouring of the original graph.

The construction runs in O(|V| + |E|) time and produces a graph with 3n
vertices and at most 3n + 3|E| edges.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeColoring instance to an IndependentSet instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "n" (int) and "edges" (list of [u, v]).

    Returns
    -------
    dict
        An IndependentSet instance with keys "n", "edges", and "k".
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])

    # New graph will have 3 copies per original vertex.
    N = n * 3
    new_edges: List[List[int]] = []

    # Helper to map (vertex, colour) -> new index
    def idx(v: int, colour: int) -> int:
        return v * 3 + colour  # colour in {0,1,2}

    # 1. Add triangle edges for each original vertex to enforce at most one colour.
    for v in range(n):
        a = idx(v, 0)
        b = idx(v, 1)
        c = idx(v, 2)
        new_edges.append([a, b])
        new_edges.append([a, c])
        new_edges.append([b, c])

    # 2. For each original edge, forbid same colour on both ends.
    for u, v in edges:
        # Ensure undirected edge appears once; input guarantees no duplicates.
        for colour in range(3):
            new_edges.append([idx(u, colour), idx(v, colour)])

    # k is the number of original vertices; we ask for an independent set of size n.
    k = n

    return {"n": N, "edges": new_edges, "k": k}

