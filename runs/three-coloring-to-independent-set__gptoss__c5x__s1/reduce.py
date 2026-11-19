"""Reduction from 3-Coloring to Independent Set.

The source problem is :class:`ThreeColoring` defined in ``problems.py``.
The target problem is :class:`IndependentSet` defined in the same file.

For a given graph G = (V, E) we construct a new graph G' = (V', E') and set
``k = |V|`` such that G is 3‑colorable iff G' has an independent set of size
at least ``k``.

Construction (standard textbook reduction):

* For every original vertex ``v`` create three vertices ``(v,0)``, ``(v,1)``
  and ``(v,2)``.  These three vertices form a triangle, i.e. they are all
  pairwise adjacent.  This forces any independent set to contain at most one
  of them – the chosen colour for ``v``.
* For every original edge ``{u, v}`` and for each colour ``c`` add an edge
  between ``(u, c)`` and ``(v, c)``.  This forbids adjacent original vertices
  from being assigned the same colour.

The resulting graph has ``3 * n`` vertices and the target ``k`` is ``n``.
The reduction runs in time O(|V| + |E|) which is polynomial.

The module provides a single function ``reduce(instance)`` which validates
the input using :class:`ThreeColoring.validate` and returns a valid instance
for :class:`IndependentSet`.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeColoring, IndependentSet, InvalidInstance


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary conforming to the ``ThreeColoring`` format.

    Returns
    -------
    dict
        A dictionary conforming to the ``IndependentSet`` format.
    """
    # Validate the source instance – will raise InvalidInstance on bad input.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # New graph will have 3*n vertices numbered as: v*3 + c where v in [0,n)
    # and c in {0,1,2}.
    new_n = 3 * n
    new_edges: List[List[int]] = []

    # 1. Add triangles for each original vertex.
    for v in range(n):
        base = 3 * v
        # edges (base, base+1), (base, base+2), (base+1, base+2)
        new_edges.append([base, base + 1])
        new_edges.append([base, base + 2])
        new_edges.append([base + 1, base + 2])

    # 2. For each original edge, add colour‑conflict edges.
    for u, v in edges:
        for c in range(3):
            new_u = 3 * u + c
            new_v = 3 * v + c
            new_edges.append([new_u, new_v])

    # Target instance: independent set of size at least n.
    target_instance = {"n": new_n, "edges": new_edges, "k": n}

    # Validate the produced target instance before returning.
    IndependentSet.validate(target_instance)
    return target_instance

