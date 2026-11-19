import random
import sys

sys.path.insert(0, ".")

from problems import HamiltonianCycle, HamiltonianPath, all_graphs, random_plain_graph
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    reduced = reduce(instance)
    # the reduction must produce a valid target instance
    HamiltonianPath.validate(reduced)
    expected = HamiltonianCycle.is_yes(instance)
    got = HamiltonianPath.is_yes(reduced)
    if expected == got:
        tests_passed += 1
    else:
        print("FAIL", instance, "->", reduced, "expected", expected, "got", got)


def main():
    # Exhaustive check over every graph on 0..6 vertices.
    for n in range(0, 7):
        for edges in all_graphs(n):
            check({"n": n, "edges": edges})

    # Random larger instances (brute force is feasible up to ~18 vertices).
    rng = random.Random(12345)
    for _ in range(200):
        scale = rng.randint(0, 12)
        check(random_plain_graph(rng, scale))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
