"""Reduction from Three-Coloring to Independent Set.

The source problem is ``ThreeColoring`` with instances of the form
``{"n": n, "edges": [[u, v], ...]}``.  The target problem is
``IndependentSet`` with instances ``{"n": n, "edges": [[u, v], ...], "k": k}``.

We implement the classic polynomial‑time reduction:

* For each vertex *v* of the original graph we create three vertices
  ``(v, 0)``, ``(v, 1)`` and ``(v, 2)`` representing the choice of one of the
  three colours.
* To enforce that at most one colour is chosen for each original vertex we
  connect the three vertices of a gadget into a triangle.
* To enforce proper colouring we forbid two adjacent original vertices from
  taking the same colour.  For every original edge ``(u, v)`` and for each
  colour ``c`` we add an edge between ``(u, c)`` and ``(v, c)``.

The constructed graph has ``3 * n`` vertices.  An independent set of size
``n`` corresponds exactly to a proper 3‑colouring of the original graph:
pick one vertex from each colour‑gadget; the independence guarantees that
adjacent original vertices receive different colours and that no vertex
chooses two colours.

The reduction runs in ``O(n + m)`` time, which is polynomial.
"""

from __future__ import annotations

from typing import Dict, List

def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeColoring instance to an IndependentSet instance.

    Parameters
    ----------
    instance: dict
        ``{"n": n, "edges": [[u, v], ...]}`` describing the input graph.

    Returns
    -------
    dict
        ``{"n": 3*n, "edges": [[u, v], ...], "k": n}`` where the edges are
        constructed as described above.
    """
    n: int = instance["n"]
    original_edges: List[List[int]] = instance.get("edges", [])

    # Number of vertices in the new graph
    new_n = 3 * n
    new_edges: List[List[int]] = []

    def add_edge(u: int, v: int) -> None:
        """Add an undirected edge (u, v) with u < v to ``new_edges``.

        The reduction format does not allow duplicate edges, but the
        construction never creates duplicates, so we simply ensure the
        ordering.
        """
        if u == v:
            return
        if u > v:
            u, v = v, u
        new_edges.append([u, v])

    # 1. Create the colour‑choice triangles for each original vertex.
    for v in range(n):
        base = v * 3
        # triangle among base, base+1, base+2
        add_edge(base, base + 1)
        add_edge(base, base + 2)
        add_edge(base + 1, base + 2)

    # 2. Add edges that forbid equal colours on adjacent original vertices.
    for u, v in original_edges:
        for colour in range(3):
            u_col = u * 3 + colour
            v_col = v * 3 + colour
            add_edge(u_col, v_col)

    # The target instance asks for an independent set of size at least n.
    return {"n": new_n, "edges": new_edges, "k": n}


# The module may be executed directly for a quick sanity check (not required
# by the task, but harmless).  It reads a JSON instance from stdin and prints
# the reduced instance.
if __name__ == "__main__":
    import json, sys
    data = json.load(sys.stdin)
    json.dump(reduce(data), sys.stdout)
