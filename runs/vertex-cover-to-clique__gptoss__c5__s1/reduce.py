"""Reduction from Vertex Cover to Clique.

The source problem is :class:`VertexCover` and the target problem is
``Clique``.  The classic polynomial‑time reduction works via the complement
graph:

* A set C of vertices is a vertex cover of size at most *k* in a graph G
  iff the complement of C is an independent set of size at least ``n - k``.
* An independent set in G is exactly a clique in the complement graph
  ``\bar G``.

Therefore we map an instance ``(n, E, k)`` of Vertex Cover to the instance
``(n, \bar E, n - k)`` of Clique, where ``\bar E`` contains every unordered
pair of distinct vertices that is **not** an edge of the original graph.

The reduction respects all edge‑cases described in the problem statements:

* If ``k < 0`` then ``n - k > n`` and the target instance asks for a clique of
  size larger than the number of vertices – which is impossible, matching the
  always‑no answer of the source.
* If ``k >= n`` then ``n - k <= 0`` and the target instance trivially asks for a
  clique of non‑positive size, which is always yes, matching the always‑yes
  answer of the source.

The function runs in ``O(n^2)`` time, polynomial in the size of the input.
"""

from __future__ import annotations

from typing import Dict, List

from problems import VertexCover, Clique


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph of a simple undirected graph.

    The input ``edges`` is guaranteed to contain each edge exactly once, with
    ``u != v`` and ``0 <= u, v < n``.  The output list also contains each edge
    exactly once, with the smaller endpoint first for determinism.
    """
    present = {frozenset((u, v)) for u, v in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in present:
                comp.append([u, v])
    return comp


def reduce(instance: Dict) -> Dict:
    """Reduce a Vertex Cover instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the VertexCover format.

    Returns
    -------
    dict
        A dictionary adhering to the Clique format such that the answer is
        *yes* for the returned instance iff it is *yes* for the input.
    """
    # Validate the source instance – this will raise InvalidInstance on bad
    # input, matching the contract of the surrounding framework.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    complement = _complement_edges(n, edges)
    new_k = n - k

    # Build the target instance dictionary.
    target_instance: Dict = {"n": n, "edges": complement, "k": new_k}

    # Validate the produced instance to catch accidental mistakes.
    Clique.validate(target_instance)
    return target_instance

