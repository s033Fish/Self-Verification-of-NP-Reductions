"""Tests for the Hamiltonian Path -> SAT reduction.

Compares problems.HamiltonianPath.is_yes on small source instances with
problems.Sat.is_yes on their reductions, and validates the produced
instances.
"""

import random
import sys

import problems
from problems import HamiltonianPath, Sat
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    out = reduce(instance)
    Sat.validate(out)
    expected = HamiltonianPath.is_yes(instance)
    got = Sat.is_yes(out)
    if expected == got:
        tests_passed += 1
    else:
        print("FAIL", instance, "expected", expected, "got", got, "->", out)
        raise AssertionError("mismatch")


def main():
    # 1. Exhaustive over all graphs on 0..5 vertices.
    for n in range(0, 6):
        for edges in problems.all_graphs(n):
            check({"n": n, "edges": edges})

    # 2. A sample of all graphs on 6 vertices (32768 total).
    rng = random.Random(999)
    pairs6 = [(u, v) for u in range(6) for v in range(u + 1, 6)]
    for _ in range(400):
        edges = [list(p) for p in pairs6 if rng.random() < 0.5]
        check({"n": 6, "edges": edges})

    # 3. Random larger instances (up to 9 vertices) with varied density.
    for _ in range(200):
        n = rng.randint(0, 9)
        p = rng.choice([0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0])
        edges = problems.random_graph(rng, n, p)
        check({"n": n, "edges": edges})

    # 4. Structured cases: paths, cycles, complete graphs, empty graphs.
    for n in range(0, 11):
        check({"n": n, "edges": []})
        check({"n": n, "edges": [[i, i + 1] for i in range(n - 1)]})
        complete = [[u, v] for u in range(n) for v in range(u + 1, n)]
        check({"n": n, "edges": complete})
        if n >= 3:
            seen = set()
            cyc = []
            for i in range(n):
                u, v = i, (i + 1) % n
                key = frozenset((u, v))
                if key not in seen:
                    seen.add(key)
                    cyc.append([u, v])
            check({"n": n, "edges": cyc})

    # 5. Edge cases explicitly.
    assert Sat.is_yes(reduce({"n": 0, "edges": []})) is False
    assert Sat.is_yes(reduce({"n": 1, "edges": []})) is True
    assert Sat.is_yes(reduce({"n": 2, "edges": []})) is False
    assert Sat.is_yes(reduce({"n": 2, "edges": [[0, 1]]})) is True

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return 0


if __name__ == "__main__":
    sys.exit(main())
