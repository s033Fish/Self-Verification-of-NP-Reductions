import random
import sys

import problems
from reduce import reduce

SOURCE = problems.ThreeColoring
TARGET = problems.ThreeSat

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    assert got == expected, (
        f"mismatch on {instance}: source={expected} target={got}\n"
        f"reduced={reduced}"
    )
    tests_passed += 1


def main():
    # 1. Every graph on up to 5 vertices (exhaustive).
    for n in range(6):
        for edges in problems.all_graphs(n):
            check({"n": n, "edges": edges})

    # 2. Random graphs on up to 9 vertices.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 9)
        p = rng.random()
        edges = problems.random_graph(rng, n, p)
        check({"n": n, "edges": edges})

    # 3. Structured graphs: complete graphs, cycles, bipartite, K4 subdivisions.
    for n in range(0, 12):
        check({"n": n, "edges": [[u, v] for u in range(n) for v in range(u + 1, n)]})
    for n in range(3, 15):
        check({"n": n, "edges": [[i, (i + 1) % n] for i in range(n)]})
    for a in range(1, 6):
        for b in range(1, 6):
            edges = [[u, a + v] for u in range(a) for v in range(b)]
            check({"n": a + b, "edges": edges})

    # 4. Edge cases explicitly.
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
