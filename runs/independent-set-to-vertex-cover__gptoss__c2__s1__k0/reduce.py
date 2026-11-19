"""Reduction from Independent Set to Vertex Cover.

The source problem (Independent Set) asks whether a given undirected graph
``G = (V, E)`` contains an independent set of size at least ``k``.  The target
problem (Vertex Cover) asks whether the same graph contains a vertex cover of
size at most ``k'``.

It is a classic textbook reduction: a set ``S ⊆ V`` is an independent set in
``G`` iff its complement ``V \ S`` is a vertex cover of ``G``.  Consequently,
``G`` has an independent set of size ``k`` ⇔ ``G`` has a vertex cover of size
``|V| - k``.

The ``reduce`` function therefore:
  * copies the number of vertices ``n`` and the edge list unchanged,
  * transforms the parameter ``k`` into ``n - k``.

All edge‑cases described in the problem statements are preserved by this
arithmetic transformation:
  - If ``k ≤ 0`` the Independent‑Set instance is always *yes*; ``n - k ≥ n``
    makes the Vertex‑Cover instance trivially *yes* because ``k' ≥ n``.
  - If ``k > n`` the Independent‑Set instance is always *no*; ``n - k < 0``
    yields a Vertex‑Cover instance that is always *no* because ``k' < 0``.
  - With no edges the transformation still works – any set of vertices is
    independent, and the complement covers all (non‑existent) edges.

The function runs in linear time with respect to the size of the input
instance (simply copying the data and performing a constant‑time arithmetic
operation), satisfying the polynomial‑time requirement.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (int), ``"edges"`` (list of ``[u, v]``),
        and ``"k"`` (int) representing an Independent Set problem.

    Returns
    -------
    dict
        A new dictionary representing the equivalent Vertex Cover problem.
        The vertex count and edge list are unchanged, and the new ``k`` is
        ``n - original_k``.
    """

    # Extract required fields.  We assume the input has been validated by the
    # framework that supplies the instance, as per the problem description.
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # The reduction is simply the complement size.
    new_k: int = n - k

    # Return a new instance dict for the Vertex Cover problem.
    return {"n": n, "edges": edges, "k": new_k}

