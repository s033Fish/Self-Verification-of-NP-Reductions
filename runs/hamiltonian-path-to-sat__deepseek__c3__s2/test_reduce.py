import itertools
import random

import problems
from problems import HamiltonianPath, Sat
from reduce import reduce

SOURCE = HamiltonianPath
TARGET = Sat


def check(instance, counter):
    """Validate, reduce, validate target, compare brute-force answers."""
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    counter[0] += 1
    if expected == got:
        counter[1] += 1
    else:
        print("MISMATCH", instance, "->", reduced, "expected", expected, "got", got)
    return expected == got


def main():
    counter = [0, 0]

    # Exhaustive: all graphs on n = 0..5 vertices.
    for n in range(0, 6):
        for edges in problems.all_graphs(n):
            check({"n": n, "edges": edges}, counter)

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(300):
        n = rng.randint(0, 8)
        edges = problems.random_graph(rng, n)
        check({"n": n, "edges": edges}, counter)

    # Dense / sparse structured cases.
    for n in range(0, 9):
        # complete graph
        complete = [[u, v] for u in range(n) for v in range(u + 1, n)]
        check({"n": n, "edges": complete}, counter)
        # empty graph
        check({"n": n, "edges": []}, counter)
        # path graph
        path = [[i, i + 1] for i in range(n - 1)]
        check({"n": n, "edges": path}, counter)
        # cycle graph
        cycle = path + ([[n - 1, 0]] if n >= 3 else [])
        check({"n": n, "edges": cycle}, counter)

    print(f"tests_run={counter[0]} tests_passed={counter[1]}")
    return counter


if __name__ == "__main__":
    counter = main()
    assert counter[0] == counter[1], "some tests failed"
