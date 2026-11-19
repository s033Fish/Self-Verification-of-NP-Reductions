"""Reduction from Vertex Cover to Clique.

The source problem (Vertex Cover) expects an instance of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

where ``n`` is the number of vertices (numbered ``0`` to ``n-1``) and
``edges`` lists each undirected edge exactly once. ``k`` is the size bound
for the vertex cover.

The target problem (Clique) uses the same representation but asks whether
the graph contains a clique of size at least ``k``.

Standard polynomial‑time reduction:

    * Build the complement graph ``G'`` of the input graph ``G``.
    * Output the same vertex set ``V`` and the complement edge set.
    * Set the new parameter ``k' = n - k``.

Correctness sketch:
    A set ``C`` is a vertex cover of size ≤ ``k`` in ``G`` iff its complement
    ``V\\C`` is an independent set of size ≥ ``n - k``.  Independent sets in a
    graph correspond to cliques in the complement graph, so ``V\\C`` is a
    clique of size ≥ ``n - k`` in ``G'``.  The construction therefore preserves
    the answer for all edge‑cases (negative ``k``, ``k ≥ n``, empty edge set,
    etc.).

The implementation runs in ``O(n^2)`` time, which is polynomial in the input
size.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to an equivalent Clique instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` describing a
        Vertex Cover instance.

    Returns
    -------
    dict
        A Clique instance with the same ``n`` and the complement edge list.
        The new ``k`` is ``n - original_k``.
    """

    n: int = instance["n"]
    original_edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build a set for O(1) edge existence checks. Store each edge as a tuple
    # (min(u, v), max(u, v)) to avoid duplication.
    edge_set = set()
    for u, v in original_edges:
        if u == v:
            # The problem statement guarantees u != v, but we guard against
            # malformed input.
            continue
        a, b = (u, v) if u < v else (v, u)
        edge_set.add((a, b))

    # Construct complement edges.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in edge_set:
                complement_edges.append([u, v])

    # New k for the Clique instance.
    new_k = n - k

    return {"n": n, "edges": complement_edges, "k": new_k}
