"""Reduction from Vertex Cover to Independent Set.

The source problem is ``VertexCover`` with instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}
The target problem is ``IndependentSet`` with the same graph representation
but the parameter ``k`` now denotes the required size of an independent set.

Observation:
    A set C ⊆ V is a vertex cover of G = (V, E) iff its complement I = V \\ C
    is an independent set of G. Consequently, G has a vertex cover of size
    at most k ⇔ G has an independent set of size at least |V| - k.

The reduction therefore keeps the graph unchanged and maps the parameter
``k`` to ``k' = n - k``.

The function ``reduce`` implements this transformation. It runs in linear time
with respect to the size of the input instance (simply copying the edge list
and performing an arithmetic operation), satisfying the polynomial‑time
requirement.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` as described
        in the ``VertexCover`` problem definition.

    Returns
    -------
    dict
        An instance for the ``IndependentSet`` problem with the same ``n``
        and ``edges`` but with the parameter ``k`` transformed to ``n - k``.
    """

    # Extract required fields. We assume the input has already been validated
    # by the surrounding framework, but we still access them safely.
    n: int = int(instance["n"])  # number of vertices
    edges: List[List[int]] = instance["edges"]  # list of undirected edges
    k: int = int(instance["k"])  # size bound for vertex cover

    # The complement independent set size.
    k_independent: int = n - k

    # Construct the target instance. The graph structure does not change.
    return {"n": n, "edges": edges, "k": k_independent}

