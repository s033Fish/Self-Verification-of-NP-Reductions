"""Reduction from Vertex Cover to Independent Set.

The source problem (``VertexCover``) asks whether a given undirected graph
has a vertex cover of size **at most** ``k``.  The target problem
(``IndependentSet``) asks whether the same graph has an independent set of
size **at least** ``k``.

For any graph ``G = (V, E)`` the complement of a vertex cover is an
independent set and vice‑versa:

    C is a vertex cover  ⇔  V \ C is an independent set.

Therefore a vertex cover of size ``k`` exists iff an independent set of size
``|V| - k`` exists.  The reduction simply keeps the graph unchanged and
transforms the parameter ``k`` accordingly.

The function ``reduce`` below implements this transformation.  It runs in
linear time with respect to the size of the instance (it merely copies the
edge list) and satisfies all edge‑case requirements inherited from the
problem specifications.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (number of vertices), ``"edges"`` (a
        list of ``[u, v]`` pairs) and ``"k"`` (the size bound for the vertex
        cover).  The instance is assumed to be validated by the ``VertexCover``
        class – the reduction does not perform its own validation to keep the
        implementation lightweight.

    Returns
    -------
    dict
        An Independent Set instance with the same graph and parameter
        ``k' = n - k``.
    """

    n: int = instance["n"]
    k: int = instance["k"]
    edges: List[List[int]] = instance["edges"]

    # Transform the parameter: a vertex cover of size ≤ k exists ⇔ an
    # independent set of size ≥ n - k exists.
    new_k: int = n - k

    # Return a new dict.  ``edges`` is a list of lists; a shallow copy is
    # sufficient because the inner lists contain only immutable ints.
    return {
        "n": n,
        "edges": [edge.copy() for edge in edges],
        "k": new_k,
    }

