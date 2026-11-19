"""Reduction from Vertex Cover to Set Cover.

The source problem (VertexCover) instance format is::

    {"n": int, "edges": [[u, v], ...], "k": int}

The target problem (SetCover) instance format is::

    {"universe_size": int, "sets": [[element, ...], ...], "k": int}

We map each edge to a distinct element of the universe (its index in the
``edges`` list). For each vertex ``v`` we create a set containing exactly the
indices of edges incident to ``v``. Selecting a vertex in a vertex cover is
equivalent to selecting the corresponding set in a set cover. Therefore a
vertex cover of size at most ``k`` exists iff a set cover of size at most
``k`` exists.

The reduction runs in linear time in the size of the graph.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes only for validation / documentation purposes.
import problems  # The file ``problems.py`` defines VertexCover and SetCover.


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a VertexCover instance to an equivalent SetCover instance.

    Parameters
    ----------
    instance:
        A dict adhering to the VertexCover specification.

    Returns
    -------
    dict
        A SetCover instance where ``universe_size`` equals the number of
        edges and each set corresponds to a vertex's incident edges.
    """
    # Validate the source instance – this will raise InvalidInstance if malformed.
    problems.VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Universe elements are 0 .. len(edges)-1, each representing an edge.
    universe_size = len(edges)

    # Build adjacency: for each vertex, collect indices of incident edges.
    vertex_sets: List[List[int]] = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        vertex_sets[u].append(idx)
        vertex_sets[v].append(idx)

    # The target instance follows the SetCover format.
    target_instance: Dict[str, Any] = {
        "universe_size": universe_size,
        "sets": vertex_sets,
        "k": k,
    }

    # Validate the produced instance to catch programming errors early.
    problems.SetCover.validate(target_instance)
    return target_instance

