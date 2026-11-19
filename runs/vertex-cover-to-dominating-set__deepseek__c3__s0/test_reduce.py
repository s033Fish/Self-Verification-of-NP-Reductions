import random

import problems
from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(inst):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(inst)
    red = reduce(inst)
    TARGET.validate(red)
    src = SOURCE.is_yes(inst)
    tgt = TARGET.is_yes(red)
    assert src == tgt, (inst, red, src, tgt)
    tests_passed += 1


def main():
    # Exhaustive small instances: all graphs up to 4 vertices, k in -1..n+1.
    for inst in SOURCE.enumerate_instances(4):
        check(inst)

    # Random instances across a range of scales.
    rng = random.Random(12345)
    for scale in range(0, 9):
        for _ in range(400):
            check(SOURCE.random_instance(rng, scale))

    # Hand-picked edge cases.
    cases = [
        {"n": 0, "edges": [], "k": -1},
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 5},
        {"n": 5, "edges": [], "k": 0},
        {"n": 5, "edges": [], "k": -3},
        {"n": 5, "edges": [[0, 1]], "k": 0},
        {"n": 5, "edges": [[0, 1]], "k": 1},
        {"n": 5, "edges": [[0, 1]], "k": -1},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
        {"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 2},
        {"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 3},
        {"n": 10, "edges": [[i, i + 1] for i in range(9)], "k": 4},
        {"n": 10, "edges": [[i, i + 1] for i in range(9)], "k": 5},
        {"n": 10, "edges": [[i, i + 1] for i in range(9)], "k": 100},
    ]
    for inst in cases:
        check(inst)

    # Random dense/sparse graphs with large k values.
    rng = random.Random(999)
    for _ in range(500):
        n = rng.randint(0, 8)
        edges = []
        seen = set()
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < 0.5:
                    edges.append([u, v])
        k = rng.randint(-3, n + 3)
        check({"n": n, "edges": edges, "k": k})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
