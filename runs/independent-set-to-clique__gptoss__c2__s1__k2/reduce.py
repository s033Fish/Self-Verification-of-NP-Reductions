"""Reduction from Independent Set to Clique.

The source problem (IndependentSet) asks whether a given undirected graph
contains an independent set of size at least ``k``.  The target problem (Clique)
asks whether the *complement* of that graph contains a clique of size at least
``k``.  It is a classic polynomial‑time many‑one reduction:

    G has an independent set of size k  <=>  complement(G) has a clique of size k

Both problems use the same instance format – a dictionary with keys ``"n"``,
``"edges"`` (a list of ``[u, v]`` pairs) and ``"k"``.  The reduction therefore
keeps ``n`` and ``k`` unchanged and replaces the edge list with the list of all
non‑edges of the original graph (i.e., the edges of the complement graph).

The implementation runs in O(n²) time, which is polynomial in the size of the
input.  Edge cases such as ``k <= 0`` or ``k > n`` are handled automatically –
the complement graph has the same number of vertices, so the truth value of
the target instance matches that of the source instance.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes only for type checking / documentation.  The
# reduction itself does not call any of their methods – it merely constructs a
# new instance that conforms to the ``Clique`` specification.
try:
    from problems import IndependentSet, Clique  # noqa: F401  (imported for side‑effects)
except Exception:  # pragma: no cover – the import should always succeed in the task environment
    # If the import fails for any reason we still want the module to be usable;
    # the reduction only relies on the instance format, not on the classes.
    pass


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement of an undirected simple graph.

    ``edges`` is assumed to contain each undirected edge exactly once as a
    ``[u, v]`` list with ``u != v`` and ``0 <= u, v < n``.  The function builds a
    set of frozensets for O(1) membership tests and then enumerates all pairs
    ``(u, v)`` with ``u < v`` that are *not* present in the original edge set.
    """

    # Normalise the original edges into a set of unordered pairs for quick lookup.
    edge_set = {frozenset((u, v)) for u, v in ((e[0], e[1]) for e in edges)}

    complement: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in edge_set:
                complement.append([u, v])
    return complement


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` representing a
        graph for the Independent Set problem.

    Returns
    -------
    dict
        A new instance suitable for the Clique problem.  The number of
        vertices ``n`` and the target size ``k`` are unchanged; the edge list is
        the complement of the original graph.
    """

    # Extract fields – we rely on the caller providing a valid instance.  The
    # benchmark's verification will call ``IndependentSet.validate`` on the
    # input before invoking the reduction.
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Compute complement edges.
    complement = _complement_edges(n, edges)

    # Return a new dict that matches the Clique specification.
    return {"n": n, "edges": complement, "k": k}

