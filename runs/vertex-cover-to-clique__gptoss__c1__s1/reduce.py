"""Reduction from Vertex Cover to Clique.

The source problem (VertexCover) expects an instance of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

where ``n`` is the number of vertices (labelled ``0`` … ``n-1``), ``edges``
is a list of unordered pairs representing the edges of the graph, and ``k``
is the size bound for the vertex cover.

The target problem (Clique) uses the same representation but asks for a
clique of size at least ``k``.

The classic polynomial‑time reduction works via graph complement:

* A set ``C`` is a vertex cover of size ``k`` in ``G`` iff the complement of
  ``C`` (i.e., the vertices not in ``C``) form an independent set of size
  ``n - k``.
* Independent sets in a graph correspond exactly to cliques in its
  complement.

Therefore ``G`` has a vertex cover of size *at most* ``k`` iff the complement
graph ``G̅`` has a clique of size *at least* ``n - k``.

The reduction is implemented in the ``reduce`` function below.  It runs in
``O(n^2)`` time, which is polynomial in the size of the input instance.
"""

from typing import Dict, List, Set, Tuple


def _edge_key(u: int, v: int) -> Tuple[int, int]:
    """Return a canonical ordered tuple for an undirected edge.

    The input instance guarantees ``u != v`` and that each unordered edge
    appears only once, but it does not guarantee a particular ordering.  By
    always storing ``(min, max)`` we can safely use a ``set`` for fast
    membership tests.
    """
    return (u, v) if u < v else (v, u)


def reduce(instance: Dict) -> Dict:
    """Reduce a Vertex Cover instance to a Clique instance.

    Parameters
    ----------
    instance: dict
        A VertexCover instance with keys ``"n"``, ``"edges"`` and ``"k"``.

    Returns
    -------
    dict
        A Clique instance that is a yes‑instance exactly when the original
        instance is a yes‑instance.
    """
    n: int = instance["n"]
    k: int = instance["k"]

    # Build a set of existing edges for O(1) look‑ups.
    original_edges: Set[Tuple[int, int]] = set()
    for u, v in instance.get("edges", []):
        original_edges.add(_edge_key(u, v))

    # Complement edges: all unordered pairs of distinct vertices that are not
    # present in the original graph.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in original_edges:
                complement_edges.append([u, v])

    # The target k is n - original_k (size of the required clique).
    target_k = n - k

    return {"n": n, "edges": complement_edges, "k": target_k}

