"""Reduction from Independent Set to Vertex Cover.

The source problem (Independent Set) and the target problem (Vertex Cover)
share the exact same graph representation.  An independent set of size
``k`` exists in a graph ``G`` with ``n`` vertices iff a vertex cover of size
``n - k`` exists in the same graph.  This classic complementarity gives a
polynomial‑time many‑one reduction.

The reduction function simply copies the ``n`` and ``edges`` fields and
stores ``k' = n - k`` as the new ``k`` field for the vertex‑cover instance.
All edge‑cases are handled automatically because:

* ``k <= 0`` → ``n - k >= n`` → vertex‑cover instance always yes.
* ``k > n`` → ``n - k < 0`` → vertex‑cover instance always no.
* For ``0 < k <= n`` the equivalence holds directly.

The implementation runs in O(1) time besides copying the edge list, which
is linear in the size of the input – polynomial in the encoding length.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` representing
        a graph and the desired independent‑set size.

    Returns
    -------
    dict
        A new instance for the Vertex Cover problem with the same graph and
        ``k' = n - k``.
    """
    # Extract fields; we assume the caller has already validated the instance
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # The reduction: complement the size requirement.
    new_k = n - k

    # Return a fresh dictionary to avoid mutating the original instance.
    return {"n": n, "edges": edges.copy(), "k": new_k}

