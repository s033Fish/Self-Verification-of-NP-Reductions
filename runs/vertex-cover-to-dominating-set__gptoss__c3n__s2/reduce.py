"""Reduction from Vertex Cover to Dominating Set.

The source problem is :class:`VertexCover` (see ``problems.py``).  An
instance is a dictionary ``{"n": n, "edges": [[u, v], ...], "k": k}``.

The target problem is :class:`DominatingSet`.  An instance has the same
format.

We implement the classic polynomial‑time reduction that introduces a new
vertex for every edge and, additionally, a leaf for each isolated vertex.

Construction
=============
Given ``G = (V, E)`` and an integer ``k``:

* Let ``iso`` be the set of isolated vertices (degree 0).
* For every edge ``e = (u, v) ∈ E`` create a new vertex ``w_e`` and add the
  edges ``(w_e, u)`` and ``(w_e, v)``.
* For every isolated vertex ``v ∈ iso`` create a leaf ``ℓ_v`` and add the edge
  ``(ℓ_v, v)``.

The new graph ``G'`` has ``n' = n + |E| + |iso|`` vertices.  The parameter is
``k' = k + |iso|`` (unless ``k < 0`` – in that case we keep ``k' = k`` so the
target instance is automatically a "no" instance, matching the source).

Correctness Sketch
------------------
*If* ``G`` has a vertex cover ``C`` of size ≤ ``k`` then the set
``D = C ∪ {ℓ_v : v ∈ iso}`` dominates ``G'`` and has size ≤ ``k'``.
*If* ``G'`` has a dominating set ``D`` of size ≤ ``k'`` then we can replace
any leaf ``ℓ_v`` in ``D`` by its neighbour ``v`` (does not increase size) and
any edge‑vertex ``w_e`` by one of its endpoints.  After discarding the forced
isolated vertices we obtain a vertex cover of ``G`` of size ≤ ``k``.

Both directions run in polynomial time, and the construction itself is clearly
polynomial.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import VertexCover, DominatingSet


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to a Dominating Set instance.

    Parameters
    ----------
    instance:
        A dict representing a Vertex Cover instance as described in
        ``problems.py``.

    Returns
    -------
    dict
        A Dominating Set instance that is a yes‑instance iff the input is a
        yes‑instance.
    """
    # Validate the source instance.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Compute degree to find isolated vertices.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    isolated = [v for v in range(n) if degree[v] == 0]
    iso_cnt = len(isolated)

    # If k is negative, the source instance is always a NO instance.
    # Preserve this property by keeping k' negative.
    if k < 0:
        new_k = k
    else:
        new_k = k + iso_cnt

    new_edges: List[List[int]] = []
    # Keep original edges – they do not hurt correctness.
    new_edges.extend([list(e) for e in edges])

    next_id = n
    # For each original edge, add a new vertex adjacent to its endpoints.
    for u, v in edges:
        w = next_id
        next_id += 1
        new_edges.append([w, u])
        new_edges.append([w, v])

    # For each isolated vertex, add a leaf.
    for v in isolated:
        leaf = next_id
        next_id += 1
        new_edges.append([leaf, v])

    new_n = next_id

    reduced_instance = {"n": new_n, "edges": new_edges, "k": new_k}
    # Validate the target instance for safety.
    DominatingSet.validate(reduced_instance)
    return reduced_instance

