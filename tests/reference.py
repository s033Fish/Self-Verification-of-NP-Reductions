"""Naive reference solvers and shared malformed inputs for the problem tests.

Each reference solver follows the problem definition literally (try every
subset, assignment, colouring or ordering), so it is slow but easy to trust.
The tests check every fast solver in benchmark/problems against these.
"""

from __future__ import annotations

from itertools import combinations, permutations, product


# --- Logic -------------------------------------------------------------------


def assignments(num_vars: int):
    """Every assignment, as a tuple where index v-1 holds variable v's value."""
    return product((False, True), repeat=num_vars)


def literal_value(values, literal: int) -> bool:
    return values[abs(literal) - 1] == (literal > 0)


def sat(num_vars: int, clauses) -> bool:
    return any(
        all(any(literal_value(values, lit) for lit in clause) for clause in clauses)
        for values in assignments(num_vars)
    )


def nae(num_vars: int, clauses) -> bool:
    return any(
        all(len({literal_value(values, lit) for lit in clause}) == 2 for clause in clauses)
        for values in assignments(num_vars)
    )


def one_in_three(num_vars: int, clauses) -> bool:
    return any(
        all(sum(values[v - 1] for v in clause) == 1 for clause in clauses)
        for values in assignments(num_vars)
    )


# --- Graphs ------------------------------------------------------------------


def edge_set(edges):
    return {frozenset(edge) for edge in edges}


def independent_set(n, edges, k) -> bool:
    if k <= 0:
        return True
    present = edge_set(edges)
    return any(
        all(frozenset(pair) not in present for pair in combinations(subset, 2))
        for subset in combinations(range(n), k)
    )


def vertex_cover(n, edges, k) -> bool:
    if k < 0:
        return False
    return any(
        all(u in subset or v in subset for u, v in edges)
        for size in range(min(k, n) + 1)
        for subset in map(set, combinations(range(n), size))
    )


def clique(n, edges, k) -> bool:
    if k <= 0:
        return True
    present = edge_set(edges)
    return any(
        all(frozenset(pair) in present for pair in combinations(subset, 2))
        for subset in combinations(range(n), k)
    )


def dominating_set(n, edges, k) -> bool:
    if k < 0:
        return False
    neighbours = {v: {v} for v in range(n)}
    for u, v in edges:
        neighbours[u].add(v)
        neighbours[v].add(u)
    return any(
        set().union(*(neighbours[v] for v in subset)) == set(range(n))
        for size in range(min(k, n) + 1)
        for subset in combinations(range(n), size)
    )


def three_coloring(n, edges) -> bool:
    return any(
        all(colours[u] != colours[v] for u, v in edges)
        for colours in product(range(3), repeat=n)
    )


def hamiltonian_path(n, edges) -> bool:
    present = edge_set(edges)
    return n >= 1 and any(
        all(frozenset(pair) in present for pair in zip(order, order[1:]))
        for order in permutations(range(n))
    )


def hamiltonian_cycle(n, edges) -> bool:
    if n < 3:
        return False
    present = edge_set(edges)
    return any(
        all(frozenset(pair) in present for pair in zip(cycle, cycle[1:] + cycle[:1]))
        for cycle in ((0, *rest) for rest in permutations(range(1, n)))
    )


# --- Sets and numbers --------------------------------------------------------


def set_cover(universe_size, sets, k) -> bool:
    if k < 0:
        return False
    universe = set(range(universe_size))
    return any(
        set().union(*(set(s) for s in chosen)) == universe
        for size in range(min(k, len(sets)) + 1)
        for chosen in combinations(sets, size)
    )


def exact_cover(universe_size, sets) -> bool:
    for size in range(len(sets) + 1):
        for chosen in combinations(sets, size):
            elements = [e for s in chosen for e in s]
            if len(elements) == len(set(elements)) and set(elements) == set(
                range(universe_size)
            ):
                return True
    return False


def subset_sum(numbers, target) -> bool:
    return any(
        sum(chosen) == target
        for size in range(len(numbers) + 1)
        for chosen in combinations(numbers, size)
    )


def partition(numbers) -> bool:
    total = sum(numbers)
    return total % 2 == 0 and subset_sum(numbers, total // 2)


# --- Shared malformed inputs -------------------------------------------------

# Structural graph errors, written without "k"; graph-with-k tests add k.
MALFORMED_GRAPHS = [
    {"n": 3, "edges": [[0, 3]]},          # vertex out of range
    {"n": 3, "edges": [[1, 1]]},          # self-loop
    {"n": 3, "edges": [[0, 1], [1, 0]]},  # duplicate edge
    {"n": 3, "edges": [[0, "1"]]},        # non-int endpoint
    {"n": 3, "edges": [[0, 1, 2]]},       # not a pair
    {"n": True, "edges": []},             # bool is not an int
    {"n": -1, "edges": []},               # negative n
    {"n": 3, "edges": "0-1"},             # edges not a list
]


def with_k(instance, k=1):
    return {**instance, "k": k}
