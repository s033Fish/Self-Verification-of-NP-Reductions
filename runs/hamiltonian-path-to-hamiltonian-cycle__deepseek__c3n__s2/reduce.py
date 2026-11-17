"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

Standard reduction: add one new vertex connected to every original vertex.
A Hamiltonian path v1..vn in the source becomes the Hamiltonian cycle
v1..vn,new,v1 in the target, and removing the new vertex from any
Hamiltonian cycle of the target leaves a Hamiltonian path of the source.

The standard reduction needs the target to have at least 3 vertices to
admit any cycle, so the tiny cases n = 0, 1, 2 are handled explicitly.
"""

from __future__ import annotations

from typing import Any


def _triangle() -> dict[str, Any]:
    return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}


def _no_instance() -> dict[str, Any]:
    # n = 0 has no Hamiltonian cycle (and no Hamiltonian path either).
    return {"n": 0, "edges": []}


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Hamiltonian Path instance to a Hamiltonian Cycle instance."""
    n = instance["n"]
    edges = instance["edges"]

    # Small cases: the target cannot have a cycle for n <= 2, so map the
    # source answer directly onto a trivially yes/no target instance.
    if n == 0:
        # Source: no.  Target: no.
        return _no_instance()
    if n == 1:
        # Source: yes.  Target: yes (triangle).
        return _triangle()
    if n == 2:
        # Source: yes iff edge [0, 1] is present.
        has_edge = any({u, v} == {0, 1} for u, v in edges)
        return _triangle() if has_edge else _no_instance()

    # n >= 3: add vertex n adjacent to every original vertex.
    new_edges = [[u, v] for u, v in edges]
    for v in range(n):
        new_edges.append([v, n])
    return {"n": n + 1, "edges": new_edges}
