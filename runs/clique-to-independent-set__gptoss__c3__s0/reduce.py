"""Reduction from Clique to Independent Set.

The classic reduction uses the complement graph: a set of vertices forms a
clique in a graph *G* iff it forms an independent set in the complement of *G*.

Both the source (Clique) and target (IndependentSet) problems share the same
instance format – a dictionary with keys "n", "edges" and "k" –
where "edges" is a list of undirected edges [u, v] with 0 <= u, v < n.

The ``reduce`` function therefore returns an instance with the same ``n`` and
``k`` but with ``edges`` replaced by the edge list of the complement graph.

The implementation relies on the helper functions defined in ``problems.py``:
``adjacency`` builds a bit‑mask adjacency list and ``complement_adjacency``
produces the complement adjacency list. From the complement adjacency we build
an edge list containing each unordered pair exactly once.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the shared utilities from the problem definitions.
from problems import adjacency, complement_adjacency


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement of the graph ``(n, edges)``.

    The helper works with the bit‑mask representation used throughout the
    benchmark code to ensure correctness and efficiency.
    """
    # Build adjacency bit‑mask for the original graph.
    adj = adjacency(n, edges)
    # Compute complement adjacency.
    comp_adj = complement_adjacency(n, adj)

    comp_edges: List[List[int]] = []
    for u in range(n):
        # Consider only vertices v > u to avoid duplicate edges.
        mask = comp_adj[u] & ~((1 << (u + 1)) - 1)
        while mask:
            low = mask & -mask
            v = low.bit_length() - 1
            comp_edges.append([u, v])
            mask ^= low
    return comp_edges


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance.

    The returned instance has the same ``n`` and ``k`` and its edge list is the
    complement of the original graph. The function runs in polynomial time –
    essentially O(n^2) – which satisfies the requirements of the task.
    """
    n = instance["n"]
    k = instance["k"]
    edges = instance["edges"]

    comp_edges = _complement_edges(n, edges)
    return {"n": n, "edges": comp_edges, "k": k}

