"""Reduction from Vertex Cover to Set Cover.

The source problem is :class:`VertexCover` (defined in ``problems.py``) and
the target problem is :class:`SetCover`.  Both problems are represented as
plain dictionaries – the exact format is documented in the docstrings of
those classes.

The reduction is the classic one:

* The *universe* of the Set‑Cover instance consists of one element for each
  edge of the input graph.  The element identifiers are ``0`` … ``m-1`` where
  ``m`` is the number of edges.
* For every vertex ``v`` (``0`` … ``n-1``) we create a set that contains the
  indices of all edges incident to ``v``.
* The budget ``k`` stays unchanged.

Correctness follows from the observation that a collection of vertices covers
all edges iff the corresponding collection of sets covers the whole universe.

The implementation validates the input using the ``validate`` method of the
source class and then constructs the target instance.  Validation of the
target is deliberately omitted – the oracle will call ``SetCover.validate``
if it wishes to ensure well‑formedness.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import VertexCover, SetCover


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex‑Cover instance to an equivalent Set‑Cover instance.

    Parameters
    ----------
    instance:
        A dictionary that conforms to the ``VertexCover`` specification.

    Returns
    -------
    dict
        A dictionary that conforms to the ``SetCover`` specification such that
        the answer to the Set‑Cover instance is *yes* iff the answer to the
        original Vertex‑Cover instance is *yes*.
    """
    # Validate the source instance – this will raise ``InvalidInstance`` if the
    # input is malformed.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # The universe consists of one element per edge.
    universe_size = len(edges)

    # Build a list of sets, one per vertex.  Each set contains the indices of
    # edges incident to that vertex.
    vertex_sets: List[List[int]] = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        vertex_sets[u].append(idx)
        vertex_sets[v].append(idx)

    # The SetCover instance expects a list of sets.  The order of the sets is
    # irrelevant for correctness, but keeping the natural vertex order makes
    # debugging easier.
    target_instance: Dict[str, Any] = {
        "universe_size": universe_size,
        "sets": vertex_sets,
        "k": k,
    }

    # Optionally validate the produced instance – the task description does not
    # require us to call ``SetCover.validate`` here, but doing so can catch bugs
    # early during development.  It is safe to keep it because the validation
    # runs in polynomial time.
    SetCover.validate(target_instance)
    return target_instance

