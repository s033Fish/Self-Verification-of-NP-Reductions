"""Reduction from VertexCover to SetCover.

The source problem is :class:`VertexCover` defined in ``problems.py``.
The target problem is :class:`SetCover` defined in the same module.

For a graph G = (V, E) we create a set‑cover instance where the universe
consists of the edges (identified by their index in the ``edges`` list) and
each vertex v corresponds to a set containing exactly those edge‑indices that
are incident to v.  A collection of vertices covers all edges iff the
corresponding collection of sets covers the whole universe, therefore a
vertex cover of size ≤ k exists iff a set cover of size ≤ k exists.

The reduction runs in time O(|V| + |E|) and respects all edge‑cases described
in the problem statements (negative k, empty edge list, etc.).
"""

from __future__ import annotations

from typing import Dict, List

from problems import VertexCover, SetCover


def reduce(instance: Dict) -> Dict:
    """Reduce a VertexCover instance to a SetCover instance.

    Parameters
    ----------
    instance:
        A dictionary that conforms to the ``VertexCover`` format.

    Returns
    -------
    dict
        A dictionary that conforms to the ``SetCover`` format.  The answer
        to the returned instance is *yes* exactly when the answer to the
        input instance is *yes*.
    """
    # Validate the source instance – this will raise ``InvalidInstance`` if
    # the format is wrong.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Universe elements correspond to edge indices 0 .. m-1 where m = len(edges).
    m = len(edges)
    universe_size = m

    # Build a list of sets, one per vertex.
    # set_i will contain the indices of edges incident to vertex i.
    vertex_sets: List[List[int]] = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        vertex_sets[u].append(idx)
        vertex_sets[v].append(idx)

    # The target instance format expects a list of sets (list of element lists).
    target_instance = {
        "universe_size": universe_size,
        "sets": vertex_sets,
        "k": k,
    }

    # Validate the produced target instance to catch programming errors early.
    SetCover.validate(target_instance)
    return target_instance

