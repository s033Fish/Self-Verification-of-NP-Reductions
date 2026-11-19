"""Reduction from Vertex Cover to Set Cover.

The reduction is classic:

* The universe of the Set‑Cover instance consists of one element for each
  edge of the input graph.
* For each vertex *v* we create a set that contains exactly those edge‑indices
  that are incident to *v*.
* The parameter *k* stays unchanged.

Formally, given a VertexCover instance `{"n": n, "edges": E, "k": k}`
with `m = len(E)` we produce a SetCover instance `{"universe_size": m,
"sets": S, "k": k}` where `S[v] = [i for i, (u, w) in enumerate(E) if u == v or w == v]`.

This transformation runs in time O(n + m) and preserves the answer:

* If the graph has a vertex cover C of size ≤ k, then the corresponding sets
  for the vertices in C cover every edge element, yielding a set‑cover of size
  ≤ k.
* Conversely, any set‑cover of size ≤ k selects at most k vertices (because each
  set corresponds to a vertex). Those vertices cover every edge, giving a vertex
  cover of size ≤ k.

The edge cases of the source problem (k < 0, empty edge set, k ≥ n) are handled
automatically by the construction and match the semantics of Set Cover.
"""

from __future__ import annotations

from typing import Dict, List

from problems import VertexCover, SetCover


def reduce(instance: Dict) -> Dict:
    """Reduce a VertexCover instance to an equivalent SetCover instance.

    Parameters
    ----------
    instance: dict
        A valid VertexCover instance as defined in ``problems.py``.

    Returns
    -------
    dict
        A SetCover instance with the same answer.
    """
    # Validate the source instance (will raise InvalidInstance if malformed).
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Universe size is the number of edges.
    m = len(edges)

    # Build a list of sets, one per vertex.
    sets: List[List[int]] = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        sets[u].append(idx)
        sets[v].append(idx)

    # The SetCover instance follows the required format.
    reduced_instance = {
        "universe_size": m,
        "sets": sets,
        "k": k,
    }

    # Validate the produced target instance.
    SetCover.validate(reduced_instance)
    return reduced_instance

