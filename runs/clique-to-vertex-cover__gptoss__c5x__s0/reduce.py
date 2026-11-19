"""Reduction from Clique to Vertex Cover.

The classic polynomial‑time reduction works on the complement graph:

* Given an instance ``G = (V, E)`` and integer ``k`` for the Clique problem,
  we construct the complement graph ``G' = (V, E')`` where ``E'`` contains exactly
  those unordered pairs of distinct vertices that are **not** edges of ``G``.
* We set ``k' = |V| - k``.

It is well‑known that ``G`` contains a clique of size at least ``k`` iff the
complement graph ``G'`` has a vertex cover of size at most ``k'``.  The reduction
preserves all edge‑cases defined in ``problems.py``:

* ``k <= 0``  → ``k' >= n`` and a vertex‑cover instance with ``k' >= n`` is
  trivially a *yes* instance.
* ``k > n``   → ``k' < 0`` and a vertex‑cover instance with ``k' < 0`` is
  trivially a *no* instance.

The function ``reduce`` validates the source instance, builds the complement
graph, and returns a target instance suitable for the ``VertexCover`` class.
"""

from __future__ import annotations

from typing import Dict, List

from problems import Clique, VertexCover


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement of an undirected simple graph.

    ``edges`` is assumed to be a list of ``[u, v]`` with ``0 <= u, v < n`` and
    ``u != v``.  The complement contains every unordered pair of distinct
    vertices that does **not** appear in ``edges``.
    """
    present = {frozenset((u, v)) for u, v in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in present:
                comp.append([u, v])
    return comp


def reduce(instance: Dict) -> Dict:
    """Reduce a Clique instance to a VertexCover instance.

    Parameters
    ----------
    instance:
        A dictionary that conforms to the ``Clique`` specification.

    Returns
    -------
    dict
        A dictionary that conforms to the ``VertexCover`` specification and
        has the same answer (yes/no) as the input instance.
    """
    # Validate the source instance – will raise InvalidInstance on malformed
    # input.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build the complement graph.
    comp_edges = _complement_edges(n, edges)

    # Target parameter k' = n - k.
    target_k = n - k

    target_instance = {"n": n, "edges": comp_edges, "k": target_k}

    # Validate the produced target instance.
    VertexCover.validate(target_instance)
    return target_instance

