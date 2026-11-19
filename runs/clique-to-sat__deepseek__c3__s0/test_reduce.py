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
    Clique.validate(instance)
    out = reduce(instance)
    Sat.validate(out)
    expected = Clique.is_yes(instance)
    got = Sat.is_yes(out)
    assert got == expected, (
        f"MISMATCH instance={instance} expected={expected} got={got} out={out}"
    )
    tests_passed += 1


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [[u, v] for idx, (u, v) in enumerate(pairs) if mask >> idx & 1]


def exhaustive_small():
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})


def random_tests():
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 9)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(e) for e in pairs if rng.random() < rng.choice([0.2, 0.5, 0.8])]
        k = rng.randint(-3, n + 3)
        check({"n": n, "edges": edges, "k": k})


def random_instance_tests():
    rng = random.Random(999)
    for _ in range(200):
        scale = rng.randint(0, 8)
        inst = Clique.random_instance(rng, scale)
        check(inst)


def enumerate_tests():
    for inst in Clique.enumerate_instances(3):
        check(inst)


def main():
    exhaustive_small()
    random_tests()
    random_instance_tests()
    enumerate_tests()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
