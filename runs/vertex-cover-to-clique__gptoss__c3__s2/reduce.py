"""Reduction from Vertex Cover to Clique.

The source problem is ``VertexCover`` and the target problem is ``Clique`` as
defined in ``problems.py``.  Both problems use the same graph representation:

    {"n": n, "edges": [[u, v], ...], "k": k}

where ``edges`` is a list of undirected edges (no duplicates, no self‑loops)
and vertices are numbered ``0..n-1``.

Standard textbook reduction:

    A set C ⊆ V is a vertex cover of size ≤ k  ⇔  V\C is an independent set of
    size ≥ n‑k  ⇔  V\C is a clique of size ≥ n‑k in the complement graph.

Thus, given an instance ``(G, k)`` of Vertex Cover we construct the complement
graph ``G̅`` and ask whether it contains a clique of size ``k' = n - k``.

The reduction preserves the answer for all edge cases described in the
docstrings of the two problems:

* ``k < 0`` → ``k' = n - k > n`` → Clique instance is a definite *no*.
* ``k >= n`` → ``k' <= 0`` → Clique instance is a definite *yes*.
* Empty edge set → complement is a complete graph, which always contains a
  clique of size ``n - k`` when ``k >= 0``.

The implementation runs in O(n²) time, which is polynomial in the size of the
input instance.
"""

from __future__ import annotations

from typing import List, Set, Tuple

# Import the problem classes only for validation (optional).  The reduction
# itself does not need to call any heavy methods.
from problems import SOURCE, TARGET


def _edge_key(u: int, v: int) -> Tuple[int, int]:
    """Return a canonical representation of an undirected edge.

    The problems guarantee that ``u != v`` and ``0 <= u, v < n``.  We store the
    edge as a sorted tuple so that ``(u, v)`` and ``(v, u)`` map to the same key.
    """

    return (u, v) if u < v else (v, u)


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph of a simple undirected graph.

    ``edges`` is a list of ``[u, v]`` pairs.  The complement contains exactly
    those unordered pairs of distinct vertices that are *not* present in the
    original edge set.
    """

    present: Set[Tuple[int, int]] = { _edge_key(u, v) for u, v in edges }
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                comp.append([u, v])
    return comp


def reduce(instance: dict) -> dict:
    """Reduce a Vertex Cover instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``VertexCover`` specification.

    Returns
    -------
    dict
        An instance of the ``Clique`` problem such that the answer to the
        Clique instance is *yes* iff the answer to the original Vertex Cover
        instance is *yes*.
    """

    # Validate the source instance – this will raise ``InvalidInstance`` if the
    # format is wrong, matching the contract of other reduction scripts.
    SOURCE.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Complement graph edges.
    comp_edges = _complement_edges(n, edges)

    # New parameter for Clique: k' = n - k.
    k_prime = n - k

    reduced_instance = {"n": n, "edges": comp_edges, "k": k_prime}

    # Validate the produced target instance (optional but helpful for debugging).
    TARGET.validate(reduced_instance)
    return reduced_instance

