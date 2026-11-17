"""Tests comparing brute-force answers on 3-Coloring instances and their
1-in-3-SAT reductions."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_three_coloring(instance: dict) -> bool:
    """True iff the graph is 3-colourable (exhaustive over 3^n colourings)."""
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        if all(colouring[u] != colouring[v] for u, v in edges):
            return True
    return False


def solve_one_in_three_sat(instance: dict) -> bool:
    """True iff some assignment makes exactly one var true per clause.

    Backtracking with pruning: variables that do not occur in any clause are
    irrelevant, and a clause is rejected as soon as it has two true variables
    or all its variables assigned without exactly one being true.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    if not clauses:
        return True

    # Only variables that actually occur matter.
    order = sorted({abs(v) for clause in clauses for v in clause})
    pos = {v: i for i, v in enumerate(order)}
    # For each clause, the positions of its variables.
    clause_pos = [tuple(pos[v] for v in clause) for clause in clauses]

    assignment = [False] * len(order)

    def rec(i: int) -> bool:
        # Check clauses whose variables are all assigned at positions < i.
        for cpos in clause_pos:
            if all(p < i for p in cpos):
                if sum(assignment[p] for p in cpos) != 1:
                    return False
        if i == len(order):
            return True
        for value in (False, True):
            assignment[i] = value
            # Early prune: any clause with two assigned true vars fails.
            bad = False
            for cpos in clause_pos:
                true_count = 0
                assigned = 0
                for p in cpos:
                    if p < i or (p == i and value):
                        assigned += 1
                        if assignment[p]:
                            true_count += 1
                if true_count > 1:
                    bad = True
                    break
            if not bad and rec(i + 1):
                return True
        assignment[i] = False
        return False

    return rec(0)


# ----------------------------------------------------------------------
# Helpers

def all_graphs(n: int):
    """All simple graphs on n labelled vertices."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random) -> dict:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def check(instance: dict, stats: dict) -> None:
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = solve_three_coloring(instance)
    got = solve_one_in_three_sat(reduced)
    stats["run"] += 1
    if expected == got:
        stats["passed"] += 1
    else:
        stats["failures"].append((instance, reduced, expected, got))


def main() -> None:
    stats = {"run": 0, "passed": 0, "failures": []}

    # Exhaustive over all graphs with n <= 4 (64 graphs for n=4).
    for n in range(0, 5):
        for g in all_graphs(n):
            check(g, stats)

    # Random graphs on more vertices.
    rng = random.Random(12345)
    for n in range(5, 9):
        for _ in range(40):
            g = random_graph(n, rng.choice([0.15, 0.3, 0.5, 0.8]), rng)
            check(g, stats)

    # Hand-picked edge cases.
    hand = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},      # triangle: yes
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]]},  # K4: no
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]},  # C4: yes
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]},  # C5: no
        {"n": 6, "edges": []},                            # empty graph: yes
        {"n": 6, "edges": [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5]]},  # star: yes
        {"n": 7, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3],
                            [4, 5], [5, 6], [6, 4]]},      # K4 + triangle: no
    ]
    for g in hand:
        check(g, stats)

    print(f"tests run:    {stats['run']}")
    print(f"tests passed: {stats['passed']}")
    if stats["failures"]:
        print("FAILURES:")
        for inst, red, exp, got in stats["failures"][:5]:
            print("  instance:", inst)
            print("  reduced :", red)
            print("  expected:", exp, "got:", got)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
