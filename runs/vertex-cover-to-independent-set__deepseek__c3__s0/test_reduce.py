import itertools
import random

import problems
from problems import VertexCover, IndependentSet
from reduce import reduce


def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for r in range(len(pairs) + 1):
        for combo in itertools.combinations(pairs, r):
            yield [list(e) for e in combo]


def main():
    tests_run = 0
    tests_passed = 0

    # Exhaustive small instances.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                src = {"n": n, "edges": edges, "k": k}
                VertexCover.validate(src)
                tgt = reduce(src)
                IndependentSet.validate(tgt)
                expected = VertexCover.is_yes(src)
                got = IndependentSet.is_yes(tgt)
                tests_run += 1
                if expected == got:
                    tests_passed += 1
                else:
                    print("MISMATCH", src, tgt, expected, got)

    # Random instances using the provided generators.
    rng = random.Random(12345)
    for _ in range(3000):
        scale = rng.randint(0, 8)
        src = VertexCover.random_instance(rng, scale)
        tgt = reduce(src)
        IndependentSet.validate(tgt)
        expected = VertexCover.is_yes(src)
        got = IndependentSet.is_yes(tgt)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH", src, tgt, expected, got)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
