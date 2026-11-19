"""Reduction from Vertex Cover to Set Cover.

The source problem is :class:`VertexCover` defined in ``problems.py``.
The target problem is :class:`SetCover` defined in the same module.

The reduction is classic:

* The universe of the Set‑Cover instance corresponds to the edges of the
  graph.  Each edge is given an index ``0 .. |E|-1``.
* For every vertex ``v`` we create a set that contains exactly those edge
  indices incident to ``v``.  Selecting a vertex in a vertex cover is
  equivalent to selecting the corresponding set in a set cover – the edge
  (universe element) is covered iff one of its endpoints is chosen.
* The budget ``k`` is kept unchanged.

The construction runs in time linear in the size of the graph, i.e. in
polynomial time.
"""

from __future__ import annotations

from typing import Dict, List

from problems import VertexCover, SetCover


def reduce(instance: Dict) -> Dict:
    """Reduce a Vertex‑Cover instance to a Set‑Cover instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Vertex‑Cover instance.  It must satisfy
        :meth:`VertexCover.validate`.

    Returns
    -------
    dict
        A dictionary representing a Set‑Cover instance.  The returned
        instance satisfies :meth:`SetCover.validate`.
    """
    # Validate the source instance – this will raise ``InvalidInstance`` if
    # the input is malformed.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Universe size is the number of edges.  If there are no edges the
    # universe is empty, which is a valid Set‑Cover instance.
    universe_size = len(edges)

    # Build a list of sets, one per vertex.  Each set contains the indices of
    # edges incident to that vertex.
    vertex_sets: List[List[int]] = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        vertex_sets[u].append(idx)
        vertex_sets[v].append(idx)

    # The target instance expects the key "sets" containing a list of sets.
    target_instance: Dict = {
        "universe_size": universe_size,
        "sets": vertex_sets,
        "k": k,
    }

    # Validate the constructed target instance to ensure we obey the format.
    SetCover.validate(target_instance)
    return target_instance
