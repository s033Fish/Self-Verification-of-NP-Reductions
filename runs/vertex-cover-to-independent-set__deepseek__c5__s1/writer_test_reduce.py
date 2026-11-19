"""Tests for the Vertex Cover -> Independent Set reduction.

Compares brute-force solvers on many small source instances and their
reductions, and checks that reductions are valid TARGET instances.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import SOURCE, TARGET
from reduce import reduce
from solvers import solve_vertex_cover, solve_independent_set

tests_run = 0
tests_passed = 0
failures = []


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    try:
        SOURCE.validate(instance)
        reduced = reduce(instance)
        TARGET.validate(reduced)
        src_ans = solve_vertex_cover(instance)
        tgt_ans = solve_independent_set(reduced)
        assert src_ans == tgt_ans, (
            f"mismatch: {instance} -> {reduced}, "
            f"source={src_ans}, target={tgt_ans}"
        )
        tests_passed += 1
    except Exception as exc:  # noqa: BLE001
        failures.append((instance, repr(exc)))


def all_graphs(n: int):
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if mask >> i & 1]
        yield edges


def main() -> None:
    global tests_run, tests_passed
    # Exhaustive: all graphs on n = 0..4 vertices, k in -2..n+2.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Randomized: n = 5..8, random edge sets and k values.
    rng = random.Random(12345)
    for _ in range(4000):
        n = rng.randint(5, 8)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(e) for e in possible if rng.random() < 0.4]
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k})

    # Explicit edge cases from the docstrings.
    edge_cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -1},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": 3},
        {"n": 3, "edges": [[0, 1]], "k": -1},
        {"n": 3, "edges": [[0, 1]], "k": 0},
        {"n": 3, "edges": [[0, 1]], "k": 1},
        {"n": 3, "edges": [[0, 1]], "k": 3},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 1},
        {"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]], "k": 1},
        {"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]], "k": 0},
    ]
    for inst in edge_cases:
        check(inst)

    # Sanity: reduction must not mutate the input.
    original = {"n": 3, "edges": [[0, 1]], "k": 1}
    snapshot = json.dumps(original, sort_keys=True)
    reduce(original)
    tests_run += 1
    if json.dumps(original, sort_keys=True) == snapshot:
        tests_passed += 1
    else:
        failures.append((original, "reduce mutated its input"))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for inst, err in failures[:20]:
        print("FAIL", inst, err)

    verdict = {
        "verified": len(failures) == 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
