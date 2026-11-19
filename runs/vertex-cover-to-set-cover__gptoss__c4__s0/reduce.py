"""Reduction from Vertex Cover to Set Cover.

The source problem is :class:`VertexCover` (instance format `{"n": n,
"edges": [[u, v], ...], "k": k}`).
The target problem is :class:`SetCover` (instance format `{"universe_size": u,
"sets": [[element, ...], ...], "k": k}`).

For a given graph ``G = (V, E)`` we construct a set‑cover instance where:

* The universe consists of one element for each edge of ``G``.  The element
  identifier is the index of the edge in the ``edges`` list.
* For each vertex ``v`` we create a set containing exactly those edge indices
  that are incident to ``v``.
* ``k`` is kept unchanged.

This is the classic polynomial‑time reduction proving that Set Cover is at
least as hard as Vertex Cover.  The construction preserves the answer for all
edge cases described in the problem statements:

* ``k < 0`` – both problems are automatically unsatisfiable.
* Empty edge set – the universe size becomes ``0``; Set Cover is trivially
  satisfiable for any ``k >= 0``.
* ``k >= n`` – selecting all vertices yields a vertex cover, and selecting all
  corresponding sets yields a set cover.

The function validates the input using the source problem's ``validate``
method and returns a dictionary that satisfies the target problem's format.
"""

from __future__ import annotations

from typing import Dict, List

from problems import VertexCover, SetCover


def reduce(instance: Dict) -> Dict:
    """Reduce a Vertex Cover instance to an equivalent Set Cover instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Vertex Cover instance. It must pass
        ``VertexCover.validate``.

    Returns
    -------
    dict
        A Set Cover instance that is a yes‑instance iff the input is a
        yes‑instance.
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # format is wrong.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Universe size is the number of edges.
    universe_size = len(edges)

    # Build a list of sets, one per vertex. Each set contains the indices of
    # edges incident to that vertex.
    vertex_sets: List[List[int]] = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        vertex_sets[u].append(idx)
        vertex_sets[v].append(idx)

    # The target instance follows the SetCover format.
    target_instance: Dict = {
        "universe_size": universe_size,
        "sets": vertex_sets,
        "k": k,
    }

    # Validate the produced instance to catch programming errors early.
    SetCover.validate(target_instance)
    return target_instance

