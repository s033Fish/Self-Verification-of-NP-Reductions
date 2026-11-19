"""Reduction from Vertex Cover to Independent Set.

The classic relationship between the two problems is that a set of vertices
forms a vertex cover of size *k* if and only if its complement forms an
independent set of size *n - k* in the same graph.  This reduction therefore
keeps the graph unchanged and simply maps the size parameter.

The implementation validates the source instance, constructs the target
instance, validates it (to catch programming errors), and returns it.
All operations are clearly polynomial‑time (linear in the size of the edge
list).
"""

from __future__ import annotations

from copy import deepcopy

# Import the problem classes defined in ``problems.py``.  The file is in the
# same directory, so a relative import works.
from problems import VertexCover, IndependentSet


def reduce(instance: dict) -> dict:
    """Reduce a VertexCover instance to an IndependentSet instance.

    Parameters
    ----------
    instance:
        A dictionary representing a VertexCover instance.  It must contain
        the keys ``"n"``, ``"edges"`` and ``"k"`` as described in the docstring
        of ``VertexCover``.

    Returns
    -------
    dict
        An IndependentSet instance that is a yes‑instance exactly when the
        input is a yes‑instance.
    """
    # Ensure the input conforms to the VertexCover specification.  This will
    # raise ``InvalidInstance`` if the instance is malformed.
    VertexCover.validate(instance)

    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # The complement size transformation.
    new_k = n - k

    # ``edges`` is a list of lists; we copy it to avoid accidental mutation of
    # the original instance.
    new_edges = deepcopy(edges)

    target_instance = {"n": n, "edges": new_edges, "k": new_k}

    # Validate the constructed IndependentSet instance – this is a safeguard
    # for development; the validator is cheap compared to the reduction.
    IndependentSet.validate(target_instance)
    return target_instance
