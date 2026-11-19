"""Reduction from Independent Set to Vertex Cover.

The source problem (Independent Set) asks whether a graph G = (V, E) has an
independent set of size at least ``k``.  The target problem (Vertex Cover) asks
whether G has a vertex cover of size at most ``k``.

For any graph the complement of an independent set is a vertex cover and
vice‑versa.  Consequently, an instance ``(V, E, k)`` of Independent Set is a
*yes*-instance iff the instance ``(V, E, |V| - k)`` of Vertex Cover is a
*yes*-instance.  This simple transformation runs in linear time and preserves
the answer for all edge‑cases described in ``problems.py``.

The function ``reduce`` implements this transformation.  It receives a
dictionary representing an Independent Set instance and returns a dictionary
representing the corresponding Vertex Cover instance.
"""

from __future__ import annotations

def reduce(instance: dict) -> dict:
    """Convert an Independent Set instance to a Vertex Cover instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"`` (number of vertices), ``"edges"`` (a
        list of ``[u, v]`` pairs) and ``"k"`` (the target size for the
        independent set).

    Returns
    -------
    dict
        A dictionary suitable for the Vertex Cover problem, with the same
        ``n`` and ``edges`` and with ``k`` replaced by ``n - k``.
    """

    # Extract required fields.  We assume the instance has already been
    # validated by the caller (the framework validates before invoking the
    # reduction), but we still access the keys directly for clarity.
    n = instance["n"]
    edges = instance["edges"]
    k_independent = instance["k"]

    # The complementary vertex‑cover size.
    k_vertex_cover = n - k_independent

    # Construct the target instance.  The format mirrors the one described in
    # ``problems.py`` for Vertex Cover.
    return {"n": n, "edges": edges, "k": k_vertex_cover}

