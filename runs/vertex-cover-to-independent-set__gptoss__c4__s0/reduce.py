"""Reduction from Vertex Cover to Independent Set.

The source problem is :class:`VertexCover` (instance format {"n": int,
"edges": List[List[int]], "k": int}).  The target problem is
``IndependentSet`` with the same graph representation but a different
parameter ``k``.

Standard graph theory tells us that a set ``C`` of vertices is a vertex
cover iff its complement ``V \ C`` is an independent set.  Consequently,
``G`` has a vertex cover of size at most ``k`` iff it has an independent
set of size at least ``n - k``.

The reduction therefore keeps the graph unchanged and maps the integer
parameter ``k`` to ``k' = n - k``.

Both problems accept any integer for ``k``; the validation logic in
``problems.py`` will handle out‑of‑range values (e.g., ``k' > n``) as per
the problem specifications.  This transformation runs in linear time
with respect to the size of the input instance.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Vertex Cover instance with keys
        ``"n"``, ``"edges"`` and ``"k"``.

    Returns
    -------
    dict
        An Independent Set instance with the same ``n`` and ``edges`` and
        ``k' = n - k``.
    """
    # The input is assumed to be validated by the caller (the oracle will
    # call ``VertexCover.validate`` before invoking this function).  We keep
    # the implementation straightforward.
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Transform the parameter as described above.
    new_k = n - k

    return {"n": n, "edges": edges, "k": new_k}

