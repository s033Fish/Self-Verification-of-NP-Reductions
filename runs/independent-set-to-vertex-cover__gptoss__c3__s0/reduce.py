"""Reduction from Independent Set to Vertex Cover.

The source problem is ``IndependentSet`` and the target problem is
``VertexCover`` (both defined in ``problems.py``).  For a graph G=(V,E) with
|V| = n and an integer k, an independent set of size at least k exists iff
the complement of that set is a vertex cover of size at most n‑k.  Therefore
the reduction simply copies the graph and replaces ``k`` with ``n - k``.

The function runs in linear time in the size of the instance and respects
all edge‑cases described in the problem specifications:

* If k <= 0 the source is always *yes*.  The reduced instance gets
  ``k' = n - k >= n`` and a vertex‑cover instance with k' >= n is also always
  *yes* (the whole vertex set is a valid cover).
* If k > n the source is always *no*.  The reduction yields ``k' = n - k < 0``
  and a vertex‑cover instance with a negative bound is defined to be *no*.
* For all other values the equivalence follows directly from the complement
  relationship.

The returned instance conforms exactly to the format required by the
``VertexCover`` class: a dictionary with keys ``"n"``, ``"edges"`` and ``"k"``.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an ``IndependentSet`` instance to a ``VertexCover`` instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (int), ``"edges"`` (list of ``[u, v]``),
        and ``"k"`` (int) representing the source Independent Set problem.

    Returns
    -------
    dict
        A new dictionary in the Vertex Cover format with the same ``n`` and
        ``edges`` and with ``k' = n - k``.
    """
    n = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k = instance["k"]

    # The reduction is simply the complement bound.
    new_k = n - k
    return {"n": n, "edges": edges, "k": new_k}

