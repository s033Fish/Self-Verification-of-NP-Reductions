import itertools
import random

from problems import DominatingSet, Sat
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    reduced = reduce(instance)
    # Validate the produced SAT instance against the documented format.
    Sat.validate(reduced)
    expected = DominatingSet.is_yes(instance)
    got = Sat.is_yes(reduced)
    if expected != got:
        print("MISMATCH", instance, "->", reduced, "expected", expected, "got", got)
        return False
    tests_passed += 1
    return True


def main():
    rng = random.Random(12345)

    # Exhaustive over all graphs on n = 0..5 vertices and all k in -1..n+1.
    for n in range(0, 6):
        pairs = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(pairs)):
            edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
            for k in range(-1, n + 2):
                if not check({"n": n, "edges": edges, "k": k}):
                    return False

    # Random larger instances.
    for _ in range(400):
        n = rng.randint(0, 9)
        edges = [
            [u, v]
            for u, v in itertools.combinations(range(n), 2)
            if rng.random() < rng.random()
        ]
        k = rng.randint(-2, n + 2)
        if not check({"n": n, "edges": edges, "k": k}):
            return False

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run == tests_passed


if __name__ == "__main__":
    ok = main()
    import json

    with open("verdict.json", "w") as f:
        json.dump({"verified": bool(ok), "tests_run": tests_run, "tests_passed": tests_passed}, f)
    print("OK" if ok else "FAILED")
