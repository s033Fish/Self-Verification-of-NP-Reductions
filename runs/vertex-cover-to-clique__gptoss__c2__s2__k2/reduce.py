"""Reduction from Vertex Cover to Clique.

The source problem (VertexCover) expects an instance of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

where ``n`` is the number of vertices (labelled ``0..n-1``), ``edges`` is a
list of undirected edges (each edge appears only once, with ``u != v``) and
``k`` is the size bound for the vertex cover.  The decision question is whether
the graph has a vertex cover of size **at most** ``k``.

The target problem (Clique) uses the same instance format but asks whether the
graph contains a clique of size **at least** ``k``.

Standard polynomial‑time reduction:

* Given ``G = (V, E)`` and integer ``k`` for Vertex Cover, construct the
  complement graph ``G' = (V, E')`` where ``E'`` contains exactly those
  unordered vertex pairs that are **not** edges of ``G``.
* Set the new target bound ``k' = |V| - k``.

Correctness:
    * If ``G`` has a vertex cover ``C`` with ``|C| ≤ k`` then the remaining
      vertices ``I = V \ C`` form an independent set of size at least ``|V|-k``.
      In the complement graph ``G'`` an independent set becomes a clique, so
      ``G'`` contains a clique of size ``|V|-k`` (or larger).
    * Conversely, a clique of size ``|V|-k`` in ``G'`` corresponds to an
      independent set of the same size in ``G``; the complement of this set is
      a vertex cover of size at most ``k``.
    * Edge‑case handling follows automatically: ``k < 0`` maps to ``k' > n``
      (always a NO instance for Clique), and ``k ≥ n`` maps to ``k' ≤ 0``
      (always a YES instance for Clique).  The reduction runs in ``O(n^2)``
      time, which is polynomial.

The ``reduce`` function below implements exactly this transformation.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to an equivalent Clique instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` representing a
        Vertex Cover instance as described in the problem statement.

    Returns
    -------
    dict
        A Clique instance with the same number of vertices, the complement
        edge set, and ``k' = n - k``.
    """

    n: int = instance["n"]
    original_edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build a set for O(1) edge existence checks. Store edges as sorted tuples.
    edge_set = set()
    for u, v in original_edges:
        if u > v:
            u, v = v, u
        edge_set.add((u, v))

    # Generate complement edges: all unordered pairs (i, j) with i < j not in edge_set.
    complement_edges: List[List[int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in edge_set:
                complement_edges.append([i, j])

    # New k for Clique problem.
    new_k = n - k

    return {"n": n, "edges": complement_edges, "k": new_k}

