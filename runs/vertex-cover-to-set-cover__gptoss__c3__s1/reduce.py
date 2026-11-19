"""Reduction from Vertex Cover to Set Cover.

The source problem (VertexCover) instance format:
    {"n": int, "edges": [[u, v], ...], "k": int}
The target problem (SetCover) instance format:
    {"universe_size": int, "sets": [[element, ...], ...], "k": int}

We map each edge to a distinct element of the universe (its index in the
``edges`` list). For each vertex we create a set containing the indices of
all edges incident to that vertex. Selecting a vertex in the cover is
equivalent to selecting the corresponding set in the set cover. The
parameter ``k`` is preserved.

Correctness follows from the standard textbook reduction and respects the
edge‑case specifications of both problems.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes to reuse their validation logic.
from problems import VertexCover, SetCover


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an equivalent SetCover instance.

    The returned instance satisfies ``SetCover.is_yes`` iff the original
    instance satisfies ``VertexCover.is_yes``.
    """
    # Validate the source instance; this will raise InvalidInstance on error.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Universe elements are the edge indices 0 .. m-1 where m = |edges|.
    m = len(edges)
    universe_size = m

    # Build a list of sets, one per vertex.
    # Each set contains the indices of edges incident to that vertex.
    vertex_sets: List[List[int]] = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        vertex_sets[u].append(idx)
        vertex_sets[v].append(idx)

    # The target instance format expects a list of sets (list of element lists).
    target_instance: Dict[str, Any] = {
        "universe_size": universe_size,
        "sets": vertex_sets,
        "k": k,
    }

    # Validate the constructed target instance to catch programming errors.
    SetCover.validate(target_instance)
    return target_instance

