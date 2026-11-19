import random

import problems
from problems import IndependentSet, Clique
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(inst):
    global tests_run, tests_passed
    tests_run += 1
    out = reduce(inst)
    # The reduction must produce a valid target instance.
    Clique.validate(out)
    expected = IndependentSet.is_yes(inst)
    got = Clique.is_yes(out)
    if expected == got:
        tests_passed += 1
    else:
        raise AssertionError(
            f"mismatch: source={inst} expected={expected} target={out} got={got}"
        )


def main():
    # Exhaustive small instances (n up to 4, all graphs, k in -1..n+1).
    for inst in IndependentSet.enumerate_instances(4):
        check(inst)

    # Random instances, including edge cases around k.
    rng = random.Random(12345)
    for scale in range(0, 9):
        for _ in range(200):
            inst = IndependentSet.random_instance(rng, scale)
            check(inst)

    # Explicit edge cases.
    for n in range(0, 6):
        for k in (-5, -1, 0, 1, n - 1, n, n + 1, n + 5):
            if k < -5:
                continue
            check({"n": n, "edges": [], "k": k})
            check({"n": n, "edges": [[u, v] for u, v in __import__("itertools").combinations(range(n), 2)], "k": k})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
