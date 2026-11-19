"""Compare brute-force solvers on source instances and their reductions."""
from __future__ import annotations

import itertools
import random

from problems import VertexCover, SetCover
from reduce import reduce
from solvers import vertex_cover_answer, set_cover_answer

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    VertexCover.validate(instance)
    reduced = reduce(instance)
    SetCover.validate(reduced)
    expected = vertex_cover_answer(instance)
    got = set_cover_answer(reduced)
    assert expected == got, (
        f"mismatch: source={instance} expected={expected} "
        f"reduced={reduced} got={got}"
    )
    TESTS_PASSED += 1


def all_graphs(n):
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if mask >> i & 1]
        yield edges


def main():
    # Exhaustive over all graphs on up to 4 vertices, all k from -2 to n+1.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 2):
                check({"n": n, "edges": edges, "k": k})

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 8)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        rng.shuffle(possible)
        m = rng.randint(0, len(possible))
        edges = [list(e) for e in possible[:m]]
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k})

    # Edge cases explicitly.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": -1})
    check({"n": 5, "edges": [], "k": 0})
    check({"n": 5, "edges": [], "k": -1})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2})
    check({"n": 4, "edges": [[0, 1], [2, 3]], "k": 1})
    check({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2})

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED


if __name__ == "__main__":
    main()
