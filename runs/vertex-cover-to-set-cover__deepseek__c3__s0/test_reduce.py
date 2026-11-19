import itertools
import random

import problems
from problems import VertexCover, SetCover
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    VertexCover.validate(instance)
    out = reduce(instance)
    SetCover.validate(out)
    expected = VertexCover.is_yes(instance)
    got = SetCover.is_yes(out)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH", instance, "->", out, "expected", expected, "got", got)
        raise AssertionError("reduction mismatch")


def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield edges


def main():
    # Exhaustive small graphs, all k values including negatives and large.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 8)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(p) for p in pairs if rng.random() < 0.4]
        k = rng.randint(-1, n + 1)
        check({"n": n, "edges": edges, "k": k})

    # Use the provided random_instance generators too.
    for scale in range(0, 7):
        for _ in range(200):
            inst = VertexCover.random_instance(rng, scale)
            check(inst)

    # Exhaustive enumeration using the provided generator.
    for scale in range(0, 4):
        for inst in VertexCover.enumerate_instances(scale):
            check(inst)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
