"""Reduction from Vertex Cover to Independent Set.

The source problem is **VertexCover** with instance format::

    {"n": n, "edges": [[u, v], ...], "k": k}

The target problem is **IndependentSet** with the same format.  The classic
polynomial‑time reduction uses the complement relationship between vertex
covers and independent sets:

    S is a vertex cover of G  <=>  V \ S is an independent set of G.

Consequently, a graph G has a vertex cover of size at most ``k`` iff it has
an independent set of size at least ``n - k``.  The reduction therefore keeps
the graph unchanged and transforms the parameter ``k`` accordingly.

The function ``reduce`` takes a VertexCover instance and returns an
IndependentSet instance with ``k_target = n - k_source``.  All edge cases are
handled automatically by this arithmetic transformation, matching the
behaviour described in the problem statements (e.g., ``k < 0`` maps to a
target ``k`` larger than ``n`` which is a guaranteed *no* for IndependentSet).
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an IndependentSet instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` representing a
        Vertex Cover problem as described in ``problems.py``.

    Returns
    -------
    dict
        An instance of Independent Set with the same vertex set and edge list,
        and with parameter ``k_target = n - k_source``.
    """

    # Extract required fields.  We deliberately avoid any validation here to
    # keep the reduction lightweight; the surrounding framework will call the
    # appropriate ``validate`` functions when needed.
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k_source: int = instance["k"]

    # The complement transformation.
    k_target: int = n - k_source

    # Construct the target instance.  The format is identical, only the
    # parameter ``k`` changes.
    return {"n": n, "edges": edges, "k": k_target}

