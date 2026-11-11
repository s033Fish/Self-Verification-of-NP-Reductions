"""Helpers shared by the graph problems: validation, generation, exact solvers.

Graphs follow base.py: {"n": n, "edges": [[u, v], ...]}, vertices 0..n-1,
simple and undirected. Solvers use bitmasks: adj[v] has bit w set when v and
w are adjacent.
"""

from __future__ import annotations

import random
from collections.abc import Iterator

from .base import (
    Instance,
    all_graphs,
    random_graph,
    require_int,
    require_keys,
    validate_graph,
)


# --- Validation ---------------------------------------------------------------


def validate_plain_graph(instance: object) -> None:
    require_keys(instance, {"n", "edges"})
    assert isinstance(instance, dict)
    validate_graph(instance)


def validate_graph_with_k(instance: object) -> None:
    require_keys(instance, {"n", "edges", "k"})
    assert isinstance(instance, dict)
    validate_graph(instance)
    require_int(instance["k"], "k")


def graph_size(instance: Instance) -> int:
    return instance["n"] + len(instance["edges"])


# --- Generation ---------------------------------------------------------------


def enumerate_graphs(scale: int) -> Iterator[Instance]:
    """Every graph on 0..scale vertices."""
    for n in range(scale + 1):
        for edges in all_graphs(n):
            yield {"n": n, "edges": edges}


def enumerate_graphs_with_k(scale: int) -> Iterator[Instance]:
    """Every graph on 0..scale vertices, with every k from 0 to n. Other k
    values are valid but answered by the edge-case rules alone."""
    for n in range(scale + 1):
        for edges in all_graphs(n):
            for k in range(n + 1):
                yield {"n": n, "edges": edges, "k": k}


def random_plain_graph(rng: random.Random, scale: int) -> Instance:
    return {"n": scale, "edges": random_graph(rng, scale)}


def random_graph_with_k(rng: random.Random, scale: int) -> Instance:
    return {"n": scale, "edges": random_graph(rng, scale), "k": rng.randint(0, scale)}


# --- Bitmask utilities --------------------------------------------------------


def adjacency(n: int, edges: list[list[int]]) -> list[int]:
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def complement_adjacency(n: int, adj: list[int]) -> list[int]:
    full = (1 << n) - 1
    return [full & ~adj[v] & ~(1 << v) for v in range(n)]


def vertices(mask: int) -> Iterator[int]:
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def is_connected(n: int, adj: list[int]) -> bool:
    if n == 0:
        return True
    seen = frontier = 1
    while frontier:
        reached = 0
        for v in vertices(frontier):
            reached |= adj[v]
        frontier = reached & ~seen
        seen |= frontier
    return seen == (1 << n) - 1


# --- Exact solvers ------------------------------------------------------------


def max_independent_set_size(n: int, adj: list[int]) -> int:
    """Exact maximum independent set by branching with memoisation.

    A vertex of degree 0 or 1 is always in some maximum independent set, so it
    is taken without branching; otherwise branch on a vertex of highest degree
    (leave it out, or take it and drop its neighbours).
    """
    memo: dict[int, int] = {}

    def solve(mask: int) -> int:
        if not mask:
            return 0
        if mask in memo:
            return memo[mask]
        branch_vertex, branch_degree = -1, -1
        for v in vertices(mask):
            degree = (adj[v] & mask).bit_count()
            if degree <= 1:
                result = 1 + solve(mask & ~(1 << v) & ~adj[v])
                memo[mask] = result
                return result
            if degree > branch_degree:
                branch_vertex, branch_degree = v, degree
        v = branch_vertex
        without = mask & ~(1 << v)
        result = max(solve(without), 1 + solve(without & ~adj[v]))
        memo[mask] = result
        return result

    return solve((1 << n) - 1)


def min_dominating_set_size(n: int, adj: list[int]) -> int:
    """Exact minimum dominating set by branch and bound.

    Some vertex in the closed neighbourhood of the lowest undominated vertex
    must be chosen; branch over those, best-first, and prune any branch that
    cannot beat the best solution found.
    """
    closed = [adj[v] | (1 << v) for v in range(n)]
    full = (1 << n) - 1
    best = n  # all vertices always dominate

    def search(dominated: int, size: int) -> None:
        nonlocal best
        if dominated == full:
            best = min(best, size)
            return
        if size + 1 >= best:
            return
        undominated = full & ~dominated
        u = (undominated & -undominated).bit_length() - 1
        options = sorted(
            vertices(closed[u]),
            key=lambda w: -(closed[w] & ~dominated).bit_count(),
        )
        for w in options:
            search(dominated | closed[w], size + 1)

    search(0, 0)
    return best


def three_colourable(n: int, adj: list[int]) -> bool:
    """Exact 3-colouring by backtracking, colouring the most constrained
    vertex first (most distinct neighbour colours, then highest degree)."""
    colours = [-1] * n
    neighbours = [list(vertices(adj[v])) for v in range(n)]

    def solve(coloured: int) -> bool:
        if coloured == n:
            return True
        chosen, chosen_key, chosen_used = -1, (-1, -1), set()
        for v in range(n):
            if colours[v] != -1:
                continue
            used = {colours[w] for w in neighbours[v] if colours[w] != -1}
            key = (len(used), len(neighbours[v]))
            if key > chosen_key:
                chosen, chosen_key, chosen_used = v, key, used
        for colour in range(3):
            if colour not in chosen_used:
                colours[chosen] = colour
                if solve(coloured + 1):
                    return True
        colours[chosen] = -1
        return False

    return solve(0)


def hamiltonian_path_exists(n: int, adj: list[int]) -> bool:
    """Exact check by dynamic programming over vertex subsets: ends[mask] is
    the set of vertices where a path through exactly `mask` can end.
    O(2^n * n^2); practical up to about 20 vertices."""
    if n == 0:
        return False
    if not is_connected(n, adj):
        return False
    ends = [0] * (1 << n)
    for v in range(n):
        ends[1 << v] = 1 << v
    for mask in range(1, 1 << n):
        for v in vertices(ends[mask]):
            for w in vertices(adj[v] & ~mask):
                ends[mask | (1 << w)] |= 1 << w
    return ends[(1 << n) - 1] != 0


def hamiltonian_cycle_exists(n: int, adj: list[int]) -> bool:
    """Exact check: paths that start at vertex 0, then close the cycle.
    A simple graph needs at least 3 vertices for a cycle."""
    if n < 3 or not is_connected(n, adj):
        return False
    ends = [0] * (1 << n)
    ends[1] = 1  # the path {0} ends at 0
    for mask in range(1, 1 << n, 2):  # odd masks: paths that contain vertex 0
        for v in vertices(ends[mask]):
            for w in vertices(adj[v] & ~mask):
                ends[mask | (1 << w)] |= 1 << w
    return bool(ends[(1 << n) - 1] & adj[0])
