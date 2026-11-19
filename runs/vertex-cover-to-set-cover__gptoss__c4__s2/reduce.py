"""Reduction from Vertex Cover to Set Cover.

The source problem is :class:`VertexCover` with instance format
``{"n": n, "edges": [[u, v], ...], "k": k}``.
The target problem is :class:`SetCover` with instance format
``{"universe_size": u, "sets": [[element, ...], ...], "k": k}``.

For a graph G = (V, E) we create a set system where each element of the
universe corresponds to an edge of G and each set corresponds to a vertex.
The set for vertex ``v`` contains exactly the indices of the edges incident
to ``v``.  A vertex cover of size at most ``k`` exists iff there is a set
cover of size at most ``k`` for the constructed instance.

The construction runs in time linear in the size of the input graph, which
is polynomial, satisfying the requirements of a polynomial‑time reduction.
"""

from __future__ import annotations

from typing import Dict, List

from problems import VertexCover, SetCover


def reduce(instance: Dict) -> Dict:
    """Reduce a VertexCover instance to a SetCover instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the VertexCover format.

    Returns
    -------
    dict
        A dictionary adhering to the SetCover format such that the answer
        (yes/no) is preserved.
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # input is malformed.  The validation helpers are part of the problem
    # definitions and are inexpensive.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Map each edge to a unique index to serve as an element of the universe.
    # The order in which we enumerate edges is deterministic (the order
    # given in the instance), which is sufficient for correctness.
    edge_index = {tuple(e): idx for idx, e in enumerate(edges)}

    # Build a list of sets, one per vertex.  Each set contains the indices of
    # edges incident to that vertex.
    sets: List[List[int]] = [[] for _ in range(n)]
    for (u, v), idx in edge_index.items():
        sets[u].append(idx)
        sets[v].append(idx)

    # The universe size equals the number of edges.
    universe_size = len(edges)

    target_instance = {
        "universe_size": universe_size,
        "sets": sets,
        "k": k,
    }

    # Validate the produced target instance to catch programming errors early.
    SetCover.validate(target_instance)
    return target_instance

