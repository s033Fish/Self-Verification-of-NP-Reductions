"""Reduction from Vertex Cover to Independent Set.

The source problem (VertexCover) asks whether a given undirected graph
has a vertex cover of size *at most* ``k``.  The target problem (IndependentSet)
asks whether the same graph has an independent set of size *at least* ``k``.

It is a classic polynomial‑time many‑one reduction to use the complement of a
vertex cover: a set of vertices is a vertex cover iff its complement is an
independent set.  Therefore, a graph with ``n`` vertices has a vertex cover of
size ``k`` exactly when it has an independent set of size ``n - k``.

The ``reduce`` function below implements this transformation.  It receives an
instance of the source problem – a dictionary with keys ``"n"``, ``"edges"``
and ``"k"`` – and returns an instance of the target problem with the same
graph and the transformed parameter ``k' = n - k``.  The transformation is
clearly polynomial (linear) in the size of the input and preserves the yes/no
answer for all edge cases described in the problem statements.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        A Vertex Cover instance with the following keys:
        - ``"n"``: number of vertices (int)
        - ``"edges"``: list of edges, each edge is a two‑element list ``[u, v]``
        - ``"k"``: the size bound for the vertex cover (int)

    Returns
    -------
    dict
        An Independent Set instance with the same vertex set and edge list,
        and with ``k' = n - k`` as the required independent‑set size.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # The transformed parameter for Independent Set.
    k_prime: int = n - k

    # Return a new dictionary; we can reuse the edges list because the
    # reduction does not modify the graph structure.
    return {
        "n": n,
        "edges": edges,
        "k": k_prime,
    }

