"""Reduction from Independent Set to Vertex Cover.

The source problem (Independent Set) asks whether a graph G has an
independent set of size at least ``k``.  The target problem (Vertex Cover)
asks whether G has a vertex cover of size at most ``k'``.

The classic polynomial‑time reduction uses the complement relationship:
the complement of an independent set is a vertex cover.  Therefore a
``k``‑independent set exists in G iff a vertex cover of size ``|V| - k``
exists in the same graph.

The ``reduce`` function simply copies the graph structure and replaces the
parameter ``k`` with ``n - k`` where ``n`` is the number of vertices.
All edge cases are handled automatically because the definition of the
target problem already treats ``k'`` appropriately (e.g., ``k' >= n`` is
always a yes‑instance).  The transformation runs in linear time in the
size of the input instance.
"""

from __future__ import annotations

from typing import Dict, Any

# Import the problem definitions to access validation helpers.
import problems


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Parameters
    ----------
    instance: dict
        A valid Independent Set instance with keys ``"n"``, ``"edges"`` and
        ``"k"``.

    Returns
    -------
    dict
        A Vertex Cover instance that is a yes‑instance exactly when the input
        is a yes‑instance.
    """
    # Validate the source instance.
    problems.SOURCE.validate(instance)

    n = instance["n"]
    k = instance["k"]

    # Perform the reduction: same graph, k' = n - k.
    reduced_instance = {
        "n": n,
        "edges": [list(edge) for edge in instance["edges"]],  # copy edges
        "k": n - k,
    }

    # Validate the target instance (optional sanity check).
    problems.TARGET.validate(reduced_instance)
    return reduced_instance

