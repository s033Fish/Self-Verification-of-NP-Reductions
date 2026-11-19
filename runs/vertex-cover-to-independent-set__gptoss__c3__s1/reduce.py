"""Reduction from Vertex Cover to Independent Set.

The classic reduction uses the complement relationship between vertex covers
and independent sets: a set S ⊆ V is a vertex cover of G = (V, E) iff V\S is an
independent set of G.  Therefore, a graph G has a vertex cover of size at most
``k`` iff it has an independent set of size at least ``|V| - k``.

The reduction is therefore trivial – we keep the graph unchanged and map the
parameter ``k`` to ``n - k``.

The function ``reduce`` takes a *VertexCover* instance and returns an
*IndependentSet* instance that satisfies the above equivalence.  All edge
cases (negative k, k ≥ n, empty graph, etc.) are handled automatically by the
parameter transformation.
"""

from __future__ import annotations

from typing import Dict, Any

# Import the problem classes defined in ``problems.py``.  They provide the
# validation utilities we can reuse.
from problems import VertexCover, IndependentSet, Instance


def reduce(instance: Instance) -> Instance:
    """Reduce a Vertex Cover instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Vertex Cover instance with keys ``"n"``,
        ``"edges"`` and ``"k"``.  The instance is assumed to be valid – the
        caller (the testing harness) validates it using ``VertexCover.validate``.

    Returns
    -------
    Instance
        A dictionary representing an Independent Set instance on the same
        graph where ``k' = n - k``.
    """
    # Ensure the source instance conforms to the VertexCover specification.
    VertexCover.validate(instance)

    n = instance["n"]
    k = instance["k"]

    # Transform the parameter according to the complement relationship.
    new_k = n - k

    reduced: Dict[str, Any] = {
        "n": n,
        "edges": list(instance["edges"]),  # shallow copy – edges are immutable lists
        "k": new_k,
    }

    # Validate the produced instance as an IndependentSet instance.  This also
    # guarantees that the output conforms to the required format.
    IndependentSet.validate(reduced)
    return reduced
