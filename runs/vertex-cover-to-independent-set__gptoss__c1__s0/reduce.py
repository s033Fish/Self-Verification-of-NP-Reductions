"""Reduction from Vertex Cover to Independent Set.

The source problem (VertexCover) instance format is:
    {"n": n, "edges": [[u, v], ...], "k": k}
where ``k`` is the maximum allowed size of a vertex cover.

The target problem (IndependentSet) instance format is the same dictionary
structure, but ``k`` now denotes the *minimum* size of an independent set.

The classic polynomial‑time reduction uses the complement relationship:
    S is a vertex cover of size ≤ k  ⇔  V\S is an independent set of size ≥ n‑k.

Thus we keep the graph unchanged and transform the parameter ``k`` to
``n - k``.  This transformation preserves the answer for all edge cases:

* ``k < 0`` → ``n - k > n`` → Independent‑Set instance is a definite "no"
  (since ``k`` exceeds the number of vertices).
* ``k ≥ n`` → ``n - k ≤ 0`` → Independent‑Set instance is a definite "yes"
  (any set of size ≤ 0 is trivially independent).
* Empty edge set behaves correctly because any subset is both a cover and
  independent set.

The function runs in linear time with respect to the size of the input
instance (simply copying the data and computing an integer subtraction).
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an IndependentSet instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` describing a
        Vertex Cover instance.

    Returns
    -------
    dict
        A dictionary representing an Independent Set instance with the same
        vertex set and edge set, but with ``k`` replaced by ``n - k``.
    """
    # Extract fields; we assume the instance has been validated elsewhere.
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Compute the transformed parameter.
    k_target: int = n - k

    # Return a new instance dict.  We make a shallow copy of edges to avoid
    # accidental mutation of the original instance.
    return {"n": n, "edges": list(edges), "k": k_target}

# The module may be imported by an external harness that expects a ``reduce``
# callable.  No top‑level test code is included to keep the file pure.
