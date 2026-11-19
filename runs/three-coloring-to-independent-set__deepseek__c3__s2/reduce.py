"""Polynomial-time reduction from 3-Coloring to Independent Set.

Construction
------------
Given a 3-Coloring instance G = (V, E) with n = |V|, build an Independent
Set instance G' = (V', E') as follows.

* For every vertex v in V and every colour c in {0, 1, 2} create a node
  (v, c).  Hence |V'| = 3n.
* For every vertex v add the three edges forming a triangle on
  (v, 0), (v, 1), (v, 2): at most one colour may be chosen for v.
* For every edge [u, v] in E and every colour c add the edge
  (u, c) -- (v, c): adjacent vertices may not share a colour.

Set k = n.

Correctness
-----------
(=>) A proper 3-colouring of G yields an independent set of G' of size n:
pick, for each vertex v, the node (v, colour(v)).  Two picked nodes for the
same v are impossible (one per vertex) and for different vertices u, v the
chosen colours differ whenever [u, v] is an edge, so no edge of G' is inside
the set.

(<=) An independent set of G' of size n must contain at most one node from
each vertex triangle, and there are n triangles, so it contains exactly one
node (v, c_v) per vertex.  For every edge [u, v] the edge (u, c) -- (v, c)
in G' forces c_u != c_v.  Thus c is a proper 3-colouring of G.

Therefore G is 3-colourable iff G' has an independent set of size at least
n.  The construction uses O(n + |E|) nodes/edges and runs in polynomial
time.
"""

from typing import Any, Dict, List


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3-Coloring instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]

    # Node id for (vertex v, colour c).
    def node(v: int, c: int) -> int:
        return 3 * v + c

    new_edges: List[List[int]] = []

    # Triangle per original vertex: at most one colour can be picked.
    for v in range(n):
        new_edges.append([node(v, 0), node(v, 1)])
        new_edges.append([node(v, 0), node(v, 2)])
        new_edges.append([node(v, 1), node(v, 2)])

    # Same colour conflicts along original edges.
    for u, v in edges:
        for c in range(3):
            new_edges.append([node(u, c), node(v, c)])

    return {"n": 3 * n, "edges": new_edges, "k": n}
