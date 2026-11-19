"""Reduction from Independent Set to Vertex Cover.

The source problem (Independent Set) asks whether a given undirected graph
has an independent set of size **at least** ``k``.  The target problem
(Vertex Cover) asks whether the same graph has a vertex cover of size **at
most** ``k'``.

For any graph ``G = (V, E)`` the complement of an independent set is a vertex
cover: if ``S`` is independent then every edge must have at least one endpoint
in ``V \ S``.  Consequently:

    exists independent set of size ≥ k   ⇔   exists vertex cover of size ≤ |V| - k

The reduction therefore simply copies the graph and replaces ``k`` with
``n - k`` where ``n`` is the number of vertices.  This transformation is
obviously polynomial‑time (linear in the size of the input) and preserves the
answer for all edge cases described in ``problems.py``.

The function ``reduce`` implements this mapping.  It expects an instance of
the source problem in the dictionary format defined in ``problems.py`` and
returns an instance of the target problem using the same format.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (int), ``"edges"`` (list of ``[u, v]``),
        and ``"k"`` (int) representing the Independent Set problem.

    Returns
    -------
    dict
        A dictionary representing the equivalent Vertex Cover instance.
        The graph (``n`` and ``edges``) is unchanged, and the new ``k`` is
        ``n - k``.
    """

    # Extract required fields.  We deliberately avoid any validation here to
    # keep the reduction lightweight; the surrounding framework will handle
    # instance validation if needed.
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Compute the vertex‑cover bound.  This works for all integer values of k,
    # including negative or larger than n, matching the edge‑case semantics.
    new_k: int = n - k

    # Return a new instance in the format expected by the Vertex Cover solver.
    return {"n": n, "edges": edges, "k": new_k}
