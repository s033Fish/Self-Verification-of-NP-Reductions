"""Reduction from Vertex Cover to Independent Set.

The classic relationship between the two problems on the *same* graph is
that a set C is a vertex cover of size ≤ k iff its complement V\C is an
independent set of size ≥ n - k. Therefore we can keep the graph unchanged
and simply transform the parameter.

The function ``reduce`` validates the source instance using the provided
``VertexCover.validate`` method, then returns a new instance suitable for the
``IndependentSet`` problem.
"""

from __future__ import annotations

from typing import Dict, Any

from problems import VertexCover, IndependentSet


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an IndependentSet instance.

    The reduction works as follows:
    * Keep the number of vertices ``n`` and the edge list unchanged.
    * Transform the size bound ``k`` to ``k' = n - k``.

    This mapping preserves the answer for all edge‑cases described in the
    problem statements:
    - ``k < 0`` → ``k' > n`` (independent‑set answer is *no*).
    - ``k >= n`` → ``k' <= 0`` (independent‑set answer is *yes*).
    - Empty edge list and any ``k`` behave correctly because any subset of
      vertices is independent.
    """

    # Validate the source instance – this will raise InvalidInstance if the
    # input is malformed.
    VertexCover.validate(instance)

    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Perform the parameter transformation.
    k_prime = n - k

    # Build the target instance. Validation of the target will be performed
    # by the caller (or by the testing harness) if needed.
    reduced_instance: Dict[str, Any] = {
        "n": n,
        "edges": edges,
        "k": k_prime,
    }

    # Optionally validate the produced instance to catch programming errors.
    IndependentSet.validate(reduced_instance)
    return reduced_instance

