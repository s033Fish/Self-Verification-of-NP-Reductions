"""Reduction from Clique to Vertex Cover.

The source problem is ``Clique`` (see its docstring in ``problems.py``) and the
target problem is ``VertexCover``.  For an instance ``G = (V, E)`` and an
integer ``k`` we construct the complement graph ``G_bar`` (i.e., all non‑edges
of ``G``) and set ``k' = n - k``.  The well‑known equivalence

    G has a clique of size ≥ k  ⇔  G_bar has a vertex cover of size ≤ n - k

holds because a set of vertices is a clique in ``G`` exactly when it is an
independent set in ``G_bar``; the complement of an independent set is a vertex
cover.

Edge‑case handling:
* ``k <= 0`` – Clique is always a *yes* instance.  We return a Vertex‑Cover
  instance with ``k' = n`` (any ``k' >= n`` is trivially a yes).
* ``k > n`` – Clique is always a *no* instance.  We return a Vertex‑Cover
  instance with ``k' = -1`` (any ``k' < 0`` is trivially a no).
* Otherwise we compute the complement edges and use ``k' = n - k``.

The function runs in O(n^2) time, which is polynomial in the size of the
input instance.
"""

from __future__ import annotations

from typing import Dict, List

# Import the problem classes so that type‑checking and validation are easy.
from problems import Clique, VertexCover


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph of a simple undirected graph.

    ``edges`` is assumed to be a list of unordered pairs ``[u, v]`` with ``u != v``
    and ``0 <= u, v < n``.  The returned list contains each missing edge exactly
    once, also as an unordered pair ``[u, v]`` with ``u < v`` for consistency.
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
        A dictionary adhering to the Clique specification:
        ``{"n": int, "edges": [[u, v], ...], "k": int}``.

    Returns
    -------
    dict
        A dictionary adhering to the VertexCover specification that is a
        *yes* instance iff the original Clique instance is a *yes* instance.
    """
    # Validate the source instance using the provided problem class.  This will
    # raise ``InvalidInstance`` if the input is malformed – the same behaviour
    # expected from a reduction.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Handle the trivial edge cases directly.
    if k <= 0:
        # Clique is always yes → produce a trivially yes VertexCover instance.
        return {"n": n, "edges": [], "k": n}
    if k > n:
        # Clique is always no → produce a trivially no VertexCover instance.
        return {"n": n, "edges": [], "k": -1}

    # General case: use the complement graph.
    comp_edges = _complement_edges(n, edges)
    k_prime = n - k
    # The target instance must satisfy the VertexCover format.
    reduced_instance: Dict = {"n": n, "edges": comp_edges, "k": k_prime}
    # Validate the resulting instance (optional but good for debugging).
    VertexCover.validate(reduced_instance)
    return reduced_instance

