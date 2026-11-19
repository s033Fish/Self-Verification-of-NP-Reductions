"""Reduction from 3-Coloring to Independent Set.

The source problem (ThreeColoring) is defined as:
    instance = {"n": n, "edges": [[u, v], ...]}
    where vertices are 0..n-1 and edges are undirected.
The target problem (IndependentSet) expects an instance of the form:
    {"n": n', "edges": [[u, v], ...], "k": k}
    where the answer is YES iff the graph contains an independent set of
    size at least k.

Standard polynomial‑time reduction:
    * For each original vertex v we create three vertices (v,0), (v,1), (v,2)
      representing the three possible colours.
    * The three vertices belonging to the same original vertex form a triangle
      (clique) so that an independent set can contain at most one of them –
      enforcing that each vertex receives exactly one colour.
    * For every original edge (u, v) and for each colour c we add an edge
      between (u,c) and (v,c).  This prevents adjacent vertices from being
      assigned the same colour.
    * We set k = n (the number of original vertices).  An independent set of
      size n in the constructed graph corresponds precisely to a proper
      3‑colouring of the original graph, and vice‑versa.

The construction runs in O(n + |E|) time and produces a graph with 3n
vertices and O(n + 3|E|) edges, which is polynomial.
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
        A dictionary with keys "n", "edges", and "k" suitable for the
        IndependentSet problem.  The returned instance is a YES‑instance iff
        the input instance is a YES‑instance of ThreeColoring.
    """

    n: int = instance["n"]
    original_edges: List[List[int]] = instance.get("edges", [])

    # New graph will have three copies of each vertex.
    new_n = 3 * n
    new_edges: List[List[int]] = []

    # 1. Add a triangle (clique of size 3) for each original vertex.
    for v in range(n):
        a = 3 * v
        b = a + 1
        c = a + 2
        new_edges.append([a, b])
        new_edges.append([a, c])
        new_edges.append([b, c])

    # 2. For each original edge, forbid using the same colour on both ends.
    for u, v in original_edges:
        for colour in range(3):
            a = 3 * u + colour
            b = 3 * v + colour
            new_edges.append([a, b])

    # The required size of the independent set is exactly the number of
    # original vertices.
    k = n

    return {"n": new_n, "edges": new_edges, "k": k}

