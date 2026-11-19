"""Tests comparing brute-force answers on source instances and reductions."""

from __future__ import annotations

import itertools

import problems
from reduce import reduce
from solvers import solve_independent_set, solve_vertex_cover


def all_graphs(n):
    """Yield all simple undirected graphs on 0..n-1 as edge lists."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for r in range(len(possible) + 1):
        for chosen in itertools.combinations(possible, r):
            yield [list(e) for e in chosen]


def run_tests():
    tests_run = 0
    tests_passed = 0
    failures = []

    for n in range(0, 7):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                inst = {"n": n, "edges": edges, "k": k}
                problems.SOURCE.validate(inst)

                reduced = reduce(inst)
                problems.TARGET.validate(reduced)

                src = solve_independent_set(inst)
                tgt = solve_vertex_cover(reduced)

                tests_run += 1
                if src == tgt:
                    tests_passed += 1
                else:
                    failures.append((inst, reduced, src, tgt))

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    tests_run, tests_passed, failures = run_tests()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for inst, reduced, src, tgt in failures[:10]:
        print("FAIL", inst, "->", reduced, "src=", src, "tgt=", tgt)
    assert not failures, f"{len(failures)} failures"
    print("ALL TESTS PASSED")
