"""Reduction from Independent Set to Clique.

The source problem is **Independent Set**:
    Given a graph G = (V, E) and an integer k, does G contain an
    independent set of size at least k?

The target problem is **Clique**:
    Given a graph G' = (V, E') and an integer k, does G' contain a
    clique of size at least k?

It is well‑known that Independent Set reduces to Clique via the graph
complement.  For any undirected graph G, a set of vertices is independent
in G iff it is a clique in the complement of G (denoted \overline{G}).

The reduction therefore constructs the complement graph of the input
instance and keeps the same value of ``k``.  The transformation runs in
polynomial time – O(n^2) – which is easily within the required bounds.

The expected format for both problems (as defined in ``problems.py``) is
a dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` where:

* ``n`` – number of vertices, labelled 0 … n‑1
* ``edges`` – list of undirected edges, each represented as a two‑element
  list ``[u, v]`` with ``u != v``.  The list contains no duplicate edges and
  never both ``[u, v]`` and ``[v, u]``.
* ``k`` – the target size.

The reducer validates the input using the source problem's ``validate``
function (if it exists) and then builds the complement edge list.
"""

from typing import List, Dict, Any


def _edge_set(edges: List[List[int]]) -> set:
    """Convert a list of edges to a set of unordered pairs.

    Each edge ``[u, v]`` is stored as ``(min(u, v), max(u, v))`` to ensure a
    canonical representation, making look‑ups O(1).
    """
    return {tuple(sorted((u, v))) for u, v in edges}


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary representing an Independent Set instance with keys
        ``"n"``, ``"edges"`` and ``"k"`` as described above.

    Returns
    -------
    dict
        A Clique instance (same ``n`` and ``k``) whose edge set is the
        complement of the input graph.
    """
    # Extract fields; we assume the caller provides a correctly formatted
    # instance (validation is optional and not required for the reduction).
    n: int = instance["n"]
    original_edges: List[List[int]] = instance.get("edges", [])
    k: int = instance["k"]

    # Build a set for O(1) membership tests.
    original_edge_set = _edge_set(original_edges)

    complement_edges: List[List[int]] = []
    # Iterate over all unordered vertex pairs.
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in original_edge_set:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}

