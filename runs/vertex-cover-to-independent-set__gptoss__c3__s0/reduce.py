"""Reduction from Vertex Cover to Independent Set.

The reduction is the classic complement transformation:

    Given a graph G = (V, E) and an integer k, a set C \subseteq V is a vertex
    cover of size at most k iff its complement I = V \ C is an independent
    set of size at least |V| - k.

Therefore we can map an instance of ``VertexCover`` to an instance of
``IndependentSet`` by keeping the graph unchanged and setting the new target
parameter ``k' = n - k``.

The mapping preserves all edge‑cases described in the problem statements:

* If k < 0 then k' > n, and ``IndependentSet`` correctly answers *no*.
* If k >= n then k' <= 0, and ``IndependentSet`` correctly answers *yes*.
* For any other k the equivalence holds by the complement argument.

The function runs in linear time in the size of the instance.
"""

from __future__ import annotations

from typing import Dict, Any

# Import the problem classes to expose the expected types and to ensure the
# instance format matches the specifications defined in ``problems.py``.
from problems import VertexCover, IndependentSet


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ``VertexCover`` instance to an ``IndependentSet`` instance.

    Parameters
    ----------
    instance: dict
        A dictionary representing a ``VertexCover`` instance. It must contain
        the keys ``"n"``, ``"edges"`` and ``"k"`` as defined in the docstring of
        :class:`VertexCover`.

    Returns
    -------
    dict
        A dictionary representing an ``IndependentSet`` instance with the same
        graph and ``k' = n - k``.
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # format is wrong. The validation is cheap (linear) and ensures we produce a
    # well‑formed target instance.
    VertexCover.validate(instance)

    n = instance["n"]
    k = instance["k"]
    # Complement the parameter.
    new_k = n - k

    # Construct the target instance. The graph (n, edges) is unchanged.
    target_instance: Dict[str, Any] = {
        "n": n,
        "edges": list(instance["edges"]),  # shallow copy to avoid mutation
        "k": new_k,
    }

    # Validate the target instance to guarantee correctness of the reduction.
    IndependentSet.validate(target_instance)
    return target_instance

