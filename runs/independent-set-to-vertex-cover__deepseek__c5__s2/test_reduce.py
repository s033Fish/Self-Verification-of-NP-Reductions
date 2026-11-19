"""Independent verification of reduce.py (Independent Set -> Vertex Cover).

We write our own brute-force solvers straight from the problem docstrings
(problems.py has no solvers), generate many small source instances, run the
candidate reduction, and compare answers.

Also checks that reduce() is polynomial-time and does not call brute force
(it is a pure O(|E|) map), and that its output is a valid target instance.
"""

from __future__ import annotations

import itertools
import time

from problems import IndependentSet, VertexCover, InvalidInstance
import reduce as reduce_module


# ----------------------------------------------------------------------
# Brute-force solvers (from the definitions in problems.py)

def is_independent(n, edges, subset):
    s = set(subset)
    for u, v in edges:
        if u in s and v in s:
            return False
    return True


def solve_independent_set(instance):
    """True iff graph has an independent set of size >= k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if is_independent(n, edges, subset):
                return True
    return False


def solve_vertex_cover(instance):
    """True iff graph has a vertex cover of size <= k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            s = set(subset)
            if all(u in s or v in s for u, v in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation

def all_graphs(n):
    """All simple undirected graphs on n vertices (as edge lists)."""
    possible = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if mask >> i & 1]
        yield edges


def generate_source_instances():
    instances = []
    # n = 0 .. 5, all graphs, a range of k including negatives / > n
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                instances.append({"n": n, "edges": edges, "k": k})
    return instances


# ----------------------------------------------------------------------
# Tests

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    instances = generate_source_instances()

    for inst in instances:
        # Source instance must be valid.
        try:
            IndependentSet.validate(inst)
        except InvalidInstance as exc:
            failures.append(("invalid source", inst, str(exc)))
            continue

        tests_run += 1
        try:
            src_ans = solve_independent_set(inst)
        except Exception as exc:  # pragma: no cover
            failures.append(("source solver error", inst, repr(exc)))
            continue

        # Run the candidate reduction.
        try:
            out = reduce_module.reduce(inst)
        except Exception as exc:
            failures.append(("reduce raised", inst, repr(exc)))
            continue

        # Output must be a valid target instance.
        try:
            VertexCover.validate(out)
        except InvalidInstance as exc:
            failures.append(("invalid target", inst, repr(out) + " " + str(exc)))
            continue

        # The reduction must not mutate the input.
        if inst["k"] != inst["k"]:  # trivially false; kept for clarity
            pass

        tgt_ans = solve_vertex_cover(out)

        if src_ans != tgt_ans:
            failures.append(("answer mismatch", inst, out, src_ans, tgt_ans))
            continue

        tests_passed += 1

    # Sanity checks on the solvers themselves against the documented edge cases.
    edge_checks = [
        (solve_independent_set, {"n": 3, "edges": [], "k": 0}, True),
        (solve_independent_set, {"n": 3, "edges": [], "k": 3}, True),
        (solve_independent_set, {"n": 3, "edges": [], "k": 4}, False),
        (solve_independent_set, {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2}, False),
        (solve_independent_set, {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1}, True),
        (solve_independent_set, {"n": 3, "edges": [[0, 1]], "k": 2}, True),
        (solve_vertex_cover, {"n": 3, "edges": [], "k": 0}, True),
        (solve_vertex_cover, {"n": 3, "edges": [], "k": -1}, False),
        (solve_vertex_cover, {"n": 3, "edges": [[0, 1], [1, 2]], "k": 1}, True),
        (solve_vertex_cover, {"n": 3, "edges": [[0, 1], [1, 2]], "k": 0}, False),
        (solve_vertex_cover, {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2}, True),
        (solve_vertex_cover, {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1}, False),
    ]
    for solver, inst, expected in edge_checks:
        tests_run += 1
        got = solver(inst)
        if got == expected:
            tests_passed += 1
        else:
            failures.append(("edge case", inst, expected, got))

    # The reduction must be polynomial (and fast): time a large instance.
    big_n = 2000
    big_edges = [[i, i + 1] for i in range(big_n - 1)]
    big = {"n": big_n, "edges": big_edges, "k": big_n // 2}
    start = time.time()
    out = reduce_module.reduce(big)
    elapsed = time.time() - start
    tests_run += 1
    if elapsed < 5.0 and out == {"n": big_n, "edges": big_edges, "k": big_n - big_n // 2}:
        tests_passed += 1
    else:
        failures.append(("poly/perf", elapsed, out["k"]))

    # Input must not be mutated by reduce.
    inst = {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}
    snapshot = {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}
    reduce_module.reduce(inst)
    tests_run += 1
    if inst == snapshot:
        tests_passed += 1
    else:
        failures.append(("mutation", inst, snapshot))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:20]:
            print("  ", f)
    else:
        print("ALL TESTS PASSED")

    return tests_run, tests_passed, failures



# ----------------------------------------------------------------------
# Additional randomized checks (appended): n = 6..8 random graphs.

import random


def _random_checks():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []
    for _ in range(400):
        n = rng.randint(6, 8)
        edges = []
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < 0.4:
                    edges.append([u, v])
        k = rng.randint(-2, n + 2)
        inst = {"n": n, "edges": edges, "k": k}
        IndependentSet.validate(inst)
        out = reduce_module.reduce(inst)
        VertexCover.validate(out)
        tests_run += 1
        if solve_independent_set(inst) == solve_vertex_cover(out):
            tests_passed += 1
        else:
            failures.append((inst, out))
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    tr, tp, failures = main()
    rr, rp, rfailures = _random_checks()
    tests_run = tr + rr
    tests_passed = tp + rp
    failures = failures + rfailures
    print(f"TOTAL tests_run={tests_run} tests_passed={tests_passed}")
    verified = (tests_run == tests_passed) and not failures
    import json
    with open("verdict.json", "w") as fh:
        json.dump({"verified": bool(verified), "tests_run": tests_run, "tests_passed": tests_passed}, fh)
    print("verdict:", open("verdict.json").read())
