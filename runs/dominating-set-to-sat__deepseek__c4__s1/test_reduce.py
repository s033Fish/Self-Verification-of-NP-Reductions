"""Tests comparing brute-force answers on source instances and reductions."""
import itertools
import sys

from problems import DominatingSet, Sat
from reduce import reduce
from solvers import solve_dominating_set, solve_sat

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    DominatingSet.validate(instance)
    target = reduce(instance)
    Sat.validate(target)
    a = solve_dominating_set(instance)
    b = solve_sat(target)
    if a == b:
        tests_passed += 1
    else:
        print("MISMATCH", instance, "source=", a, "target=", b, "red=", target)
        raise AssertionError("mismatch")


def all_graphs(n):
    """All simple undirected graphs on n labelled vertices."""
    possible = list(itertools.combinations(range(n), 2))
    for r in range(len(possible) + 1):
        for subset in itertools.combinations(possible, r):
            yield [list(e) for e in subset]


def main():
    # Exhaustive small graphs, many k values including negatives and >= n.
    for n in range(0, 5):
        ks = list(range(-2, n + 3))
        for edges in all_graphs(n):
            for k in ks:
                check({"n": n, "edges": edges, "k": k})

    # A few random-ish larger graphs on 5-6 vertices with various k.
    import random
    random.seed(12345)
    for trial in range(400):
        n = random.randint(0, 6)
        possible = list(itertools.combinations(range(n), 2))
        edges = [list(e) for e in possible if random.random() < 0.4]
        k = random.randint(-1, n + 1)
        check({"n": n, "edges": edges, "k": k})

    # Explicit edge cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": 5})
    check({"n": 3, "edges": [], "k": 0})   # isolated vertices -> no
    check({"n": 3, "edges": [], "k": 3})   # yes
    check({"n": 3, "edges": [], "k": 2})   # no (3 isolated)
    check({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2})  # yes
    check({"n": 4, "edges": [[0, 1], [2, 3]], "k": 1})  # no
    check({"n": 1, "edges": [], "k": -1})  # no

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
