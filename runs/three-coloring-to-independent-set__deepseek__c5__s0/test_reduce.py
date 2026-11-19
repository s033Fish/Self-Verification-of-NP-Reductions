"""Independent verification of reduce.py: 3-Coloring -> Independent Set.

We implement our own brute-force solvers for both problems directly from the
definitions in problems.py, generate many small source instances, reduce them
with reduce.reduce, and compare the answers.  We also validate that every
reduced instance is a well-formed IndependentSet instance.
"""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET, InvalidInstance
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions
# ----------------------------------------------------------------------

def solve_three_coloring(instance: dict) -> bool:
    """True iff the graph is 3-colourable (backtracking)."""
    n = instance["n"]
    edges = instance["edges"]
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    color = [-1] * n

    def bt(i: int) -> bool:
        if i == n:
            return True
        for c in range(3):
            ok = True
            for j in adj[i]:
                if color[j] == c:
                    ok = False
                    break
            if ok:
                color[i] = c
                if bt(i + 1):
                    return True
                color[i] = -1
        return False

    return bt(0)


def max_independent_set_size(instance: dict) -> int:
    """Size of a maximum independent set (branch and bound)."""
    n = instance["n"]
    edges = instance["edges"]
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u

    best = 0

    def rec(candidates: int, current: int) -> None:
        nonlocal best
        if current > best:
            best = current
        # Bound: even taking every remaining candidate cannot beat best.
        if current + bin(candidates).count("1") <= best:
            return
        if candidates == 0:
            return
        # Branch on the lowest-numbered candidate.
        v = (candidates & -candidates).bit_length() - 1
        rest = candidates & ~(1 << v)
        # Exclude v.
        rec(rest, current)
        # Include v.
        rec(rest & ~adj[v], current + 1)

    rec((1 << n) - 1, 0)
    return best


def solve_independent_set(instance: dict) -> bool:
    """True iff there is an independent set of size >= k."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    return max_independent_set_size(instance) >= k


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_graphs(n: int):
    """All simple undirected graphs on n labelled vertices."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask & (1 << i)]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random) -> dict:
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < p:
            edges.append([u, v])
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def check_instance(inst: dict) -> bool:
    """Compare source answer with reduced-instance answer; validate format."""
    src_ans = solve_three_coloring(inst)
    red = reduce_mod.reduce(inst)

    # The reduction must return a valid TARGET instance.
    TARGET.validate(red)

    tgt_ans = solve_independent_set(red)
    return src_ans == tgt_ans


def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    def run(inst: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            ok = check_instance(inst)
        except Exception as exc:  # noqa: BLE001
            failures.append((inst, f"exception: {exc!r}"))
            return
        if ok:
            tests_passed += 1
        else:
            failures.append((inst, "answer mismatch"))

    # Exhaustive over all graphs for n = 0..5.
    for n in range(0, 6):
        for g in all_graphs(n):
            run(g)

    # Random graphs for larger n.
    rng = random.Random(12345)
    for n in (6, 7, 8):
        for _ in range(400):
            p = rng.choice([0.0, 0.15, 0.3, 0.5, 0.7, 0.9, 1.0])
            run(random_graph(n, p, rng))

    # Explicit edge cases from the definitions.
    edge_cases = [
        {"n": 0, "edges": []},                                  # yes
        {"n": 1, "edges": []},                                  # yes
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},            # triangle yes
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0],
                           [0, 2], [1, 3]]},                    # K4 no
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]},            # path yes
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4],
                           [4, 0], [0, 2], [1, 3], [2, 4],
                           [3, 0], [4, 1]]},                    # K5 no
        {"n": 6, "edges": [[0, 1], [2, 3], [4, 5]]},            # matching yes
    ]
    for g in edge_cases:
        run(g)

    # Sanity: our solvers agree with the documented edge cases.
    assert solve_three_coloring({"n": 0, "edges": []}) is True
    assert solve_three_coloring(
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]]}
    ) is False
    assert solve_independent_set({"n": 0, "edges": [], "k": 0}) is True
    assert solve_independent_set({"n": 3, "edges": [], "k": 4}) is False
    assert solve_independent_set({"n": 3, "edges": [], "k": 3}) is True

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for inst, why in failures[:10]:
            print("  ", why, inst)
    else:
        print("All tests passed.")


if __name__ == "__main__":
    main()
