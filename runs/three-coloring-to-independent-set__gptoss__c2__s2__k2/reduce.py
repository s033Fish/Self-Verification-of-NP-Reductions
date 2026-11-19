"""Reduction from ThreeColoring to IndependentSet.

The source problem *ThreeColoring* asks whether a given undirected graph
G=(V,E) can be coloured with three colours such that adjacent vertices receive
different colours.

The target problem *IndependentSet* asks, for a graph H=(V',E') and an integer
``k``, whether H contains an independent set of size at least ``k``.

Standard polynomial‑time reduction:

* For each original vertex ``v`` we create three vertices ``(v,0)``,
  ``(v,1)`` and ``(v,2)`` representing the three possible colours.
* The three vertices belonging to the same original vertex form a triangle –
  they are pairwise adjacent.  Consequently an independent set can contain at
  most one of them, enforcing that each original vertex receives at most one
  colour.
* For every edge ``{u,v}`` in the original graph we forbid assigning the same
  colour to both endpoints by connecting ``(u,c)`` with ``(v,c)`` for each
  colour ``c``.

With this construction the original graph is 3‑colourable **iff** the new
graph has an independent set of size exactly ``|V|`` (one vertex per original
vertex).  Therefore we set ``k = |V|``.

The function ``reduce`` implements this transformation.  It runs in linear
time with respect to the size of the input graph and returns an instance that
conforms to the format required by ``problems.py`` for the *IndependentSet*
problem.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeColoring instance to an IndependentSet instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"`` (number of vertices) and ``"edges"``
        (list of ``[u, v]`` pairs).  The format matches the ``ThreeColoring``
        definition in ``problems.py``.

    Returns
    -------
    dict
        An IndependentSet instance with keys ``"n"``, ``"edges"`` and ``"k"``.
        ``"n"`` is three times the original number of vertices, ``"edges"``
        contains the constructed edges as described above, and ``"k"`` is the
        original ``n``.
    """

    n: int = instance.get("n", 0)
    original_edges: List[List[int]] = instance.get("edges", [])

    # New graph will have 3 vertices for each original vertex.
    new_n = n * 3
    new_edges: List[List[int]] = []

    # Helper to map (vertex, colour) to new index.
    def idx(v: int, colour: int) -> int:
        return v * 3 + colour

    # 1. Add the triangles for each original vertex (forcing at most one colour).
    for v in range(n):
        a = idx(v, 0)
        b = idx(v, 1)
        c = idx(v, 2)
        new_edges.append([a, b])
        new_edges.append([a, c])
        new_edges.append([b, c])

    # 2. For each original edge, forbid equal colours on its endpoints.
    for u, v in original_edges:
        for colour in range(3):
            new_edges.append([idx(u, colour), idx(v, colour)])

    # The independent set size we require is exactly one vertex per original
    # vertex.
    k = n

    return {"n": new_n, "edges": new_edges, "k": k}

