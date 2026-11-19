import itertools
import random

import problems
from problems import Clique, Sat
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    reduced = reduce(instance)
    # Both must validate.
    Clique.validate(instance)
    Sat.validate(reduced)
    expected = Clique.is_yes(instance)
    got = Sat.is_yes(reduced)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH")
        print("  instance:", instance)
        print("  expected:", expected, " got:", got)
        print("  reduced:", reduced)
    return expected == got


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [[u, v] for i, (u, v) in enumerate(pairs) if mask >> i & 1]


def exhaustive():
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})


def randomized():
    rng = random.Random(12345)
    for _ in range(4000):
        n = rng.randint(0, 7)
        edges = [
            [u, v]
            for u, v in itertools.combinations(range(n), 2)
            if rng.random() < rng.random()
        ]
        k = rng.randint(-1, n + 2)
        check({"n": n, "edges": edges, "k": k})


def random_instances_from_problems():
    rng = random.Random(999)
    for scale in range(0, 7):
        for _ in range(50):
            inst = Clique.random_instance(rng, scale)
            check(inst)


if __name__ == "__main__":
    exhaustive()
    randomized()
    random_instances_from_problems()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"
    print("ALL TESTS PASSED")
