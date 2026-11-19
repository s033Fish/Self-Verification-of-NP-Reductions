"""Reduction from Vertex Cover to Set Cover.

The reduction is the classic one:

* The universe of the Set Cover instance consists of one element for each
  edge of the input graph.  We index the edges from ``0`` to ``m-1`` where
  ``m = len(edges)``.
* For every vertex ``v`` we create a set that contains exactly the indices of
  the edges incident to ``v``.
* The budget ``k`` is kept unchanged.

Correctness sketch:
    *If* the graph has a vertex cover of size at most ``k``, selecting the
    corresponding vertex‑sets covers every edge element, giving a set cover of
    size at most ``k``.
    *Conversely*, any set cover of size at most ``k`` must consist of vertex‑
    sets (by construction) and therefore the vertices whose sets were chosen
    form a vertex cover of size at most ``k``.

Both directions respect the edge‑cases described in the problem statements:
negative ``k`` stays negative, an empty edge list yields an empty universe,
and ``k >= n`` trivially works because we may select all vertex‑sets.

The implementation validates the input using the provided ``VertexCover``
class and returns a dictionary that conforms to the ``SetCover`` format.
"""

from __future__ import annotations

from typing import Dict, List

from problems import VertexCover, SetCover


def reduce(instance: Dict) -> Dict:
    """Reduce a Vertex Cover instance to an equivalent Set Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` as defined by
        :class:`VertexCover`.

    Returns
    -------
    dict
        A Set Cover instance with keys ``"universe_size"``, ``"sets"`` and
        ``"k"``.
    """
    # Validate the input – this will raise InvalidInstance if malformed.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Universe elements correspond to edges.  The size is the number of edges.
    universe_size = len(edges)

    # Build adjacency lists mapping each vertex to the set of incident edge indices.
    incident: List[List[int]] = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        incident[u].append(idx)
        incident[v].append(idx)

    # The sets for Set Cover are exactly the incident edge lists for each vertex.
    sets: List[List[int]] = incident

    # Assemble the target instance.
    reduced_instance = {
        "universe_size": universe_size,
        "sets": sets,
        "k": k,
    }

    # Validate the produced instance to ensure we obey the SetCover format.
    SetCover.validate(reduced_instance)
    return reduced_instance

