"""Reduction from Independent Set to Vertex Cover.

The classic complement reduction works as follows:

* Given a graph G = (V, E) and an integer k, an independent set of size
  at least k exists **iff** the complement set V\S is a vertex cover of
  size at most |V| - k.

Therefore we can map an ``IndependentSet`` instance to a ``VertexCover``
instance by keeping the graph unchanged and setting ``k' = n - k``.

The reduction is clearly polynomial‑time (O(1) work besides copying the
input), and it respects all edge‑cases described in the problem
specifications:

* ``k <= 0`` → ``k' >= n`` → vertex‑cover instance is trivially yes.
* ``k > n`` → ``k' < 0`` → vertex‑cover instance is trivially no.
* No edges → both problems are trivial and the transformation still
  yields equivalent answers.

The module defines a single function ``reduce(instance)`` that takes a
valid ``IndependentSet`` instance and returns a valid ``VertexCover``
instance.
"""

from __future__ import annotations

from typing import Dict, List, Any

from problems import IndependentSet, VertexCover, InvalidInstance


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an ``IndependentSet`` instance to a ``VertexCover`` instance.

    Parameters
    ----------
    instance:
        A dictionary representing an ``IndependentSet`` problem. It must
        conform to the format validated by ``IndependentSet.validate``.

    Returns
    -------
    dict
        A dictionary representing the equivalent ``VertexCover`` problem.
        The graph (``n`` and ``edges``) is unchanged and ``k`` is set to
        ``n - original_k``.
    """
    # Validate the source instance first – this will raise ``InvalidInstance``
    # if the input is malformed, matching the behaviour of other problem
    # modules.
    IndependentSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k_original: int = instance["k"]

    # Compute the target k. The arithmetic works for all integer values of k.
    k_target: int = n - k_original

    # Build the target instance. The format is identical to the source, so
    # we can reuse the same ``edges`` list (they are immutable in the sense
    # that we do not modify them).
    target_instance: Dict[str, Any] = {
        "n": n,
        "edges": edges,
        "k": k_target,
    }

    # Validate the target instance to ensure we have produced a well‑formed
    # ``VertexCover`` problem. This also guarantees that the reduction does
    # not accidentally produce an invalid output.
    VertexCover.validate(target_instance)

    return target_instance

