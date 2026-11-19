"""Reduction from Vertex Cover to Independent Set.

The source problem (VertexCover) asks whether a given undirected graph
has a vertex cover of size at most ``k``.  The target problem (IndependentSet)
asks whether the same graph has an independent set of size at least ``k``.

Classic complementarity: a set of vertices is a vertex cover **iff** its
complement is an independent set.  Therefore a graph has a vertex cover of
size ≤ k exactly when it has an independent set of size ≥ n‑k, where ``n``
is the number of vertices.

The reduction is therefore trivial: keep the graph unchanged and map the
parameter ``k`` to ``n - k``.

The function below follows the interface required by the evaluation harness:

```
def reduce(instance) -> instance:
    """Transform a VertexCover instance into an IndependentSet instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` representing
        a VertexCover instance as described in ``problems.py``.

    Returns
    -------
    dict
        An IndependentSet instance that is a yes‑instance exactly when the
        input instance is a yes‑instance.
    """
```

The transformation runs in O(|V|+|E|) time, i.e., polynomial time.
"""

from __future__ import annotations

def reduce(instance):
    """Reduce Vertex Cover to Independent Set.

    Given a VertexCover instance ``{n, edges, k}``, return an IndependentSet
    instance ``{n, edges, n - k}``.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # The complement transformation: independent set size >= n - k.
    new_k = n - k

    return {"n": n, "edges": edges, "k": new_k}
