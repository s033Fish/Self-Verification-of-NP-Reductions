"""Reduction from Independent Set to Vertex Cover.

The classical reduction uses the complement relationship:

    S ⊆ V is an independent set  ⇔  V \ S is a vertex cover.

Therefore, an instance {"n": n, "edges": E, "k": k} of Independent
Set can be mapped to the Vertex Cover instance {"n": n, "edges": E,
"k": n - k}.  This transformation preserves the answer for all edge
cases described in the problem specifications:

* ``k <= 0`` → ``n - k >= n`` → vertex‑cover instance with ``k >= n`` which
  is always a yes‑instance.
* ``k > n`` → ``n - k < 0`` → vertex‑cover instance with ``k < 0`` which is
  always a no‑instance.

Both the source and target problems share the exact same graph format, so we
simply copy the ``n`` and ``edges`` fields.

The ``reduce`` function validates the source instance using the IndependentSet
class (to catch malformed inputs) and then returns the transformed instance.
"""

from __future__ import annotations

from typing import Dict, Any

# Import the problem classes defined in ``problems.py``.
from problems import IndependentSet, VertexCover


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary representing an Independent Set instance with keys
        ``"n"``, ``"edges"`` and ``"k"``.

    Returns
    -------
    dict
        A Vertex Cover instance with the same graph and ``k' = n - k``.
    """
    # Validate the source instance. This will raise ``InvalidInstance`` if the
    # input does not conform to the specification.
    IndependentSet.validate(instance)

    n = instance["n"]
    k = instance["k"]

    # The reduction is simply the complement of the independent set size.
    new_k = n - k

    # Return a fresh dict to avoid accidental mutation of the original.
    return {
        "n": n,
        "edges": list(instance["edges"]),  # shallow copy of the edge list
        "k": new_k,
    }

