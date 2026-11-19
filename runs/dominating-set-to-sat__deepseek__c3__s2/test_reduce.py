"""Tests for the Dominating Set -> SAT reduction in reduce.py."""

import itertools
import random
import sys

import problems
from problems import DominatingSet, Sat
from reduce import reduce

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    DominatingSet.validate(instance)
    target = reduce(instance)
    Sat.validate(target)
    expected = DominatingSet.is_yes(instance)
    got = Sat.is_yes(target)
    if expected != got:
        print("MISMATCH")
        print("  source:", instance)
        print("  expected:", expected, "got:", got)
        print("  target:", target)
        return False
    TESTS_PASSED += 1
    return True


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [list(p) for i, p in enumerate(pairs) if mask >> i & 1]


def test_exhaustive_small():
    ok = True
    # every graph on 0..4 vertices, every k from -1 to n+1
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-1, n + 2):
                ok &= check({"n": n, "edges": edges, "k": k})
    return ok


def test_random():
    ok = True
    rng = random.Random(12345)
    for _ in range(4000):
        n = rng.randint(0, 8)
        pairs = list(itertools.combinations(range(n), 2))
        p = rng.random()
        edges = [list(e) for e in pairs if rng.random() < p]
        k = rng.randint(-2, n + 2)
        ok &= check({"n": n, "edges": edges, "k": k})
    return ok


def test_target_random_instances():
    """Sanity: Sat solver agrees with brute force on random SAT instances."""
    ok = True
    global TESTS_RUN, TESTS_PASSED
    rng = random.Random(999)
    for _ in range(1000):
        TESTS_RUN += 1
        m = rng.randint(0, 6)
        clauses = []
        for _ in range(rng.randint(0, 8)):
            length = rng.randint(0, 4)
            clause = []
            for _ in range(length):
                if m == 0:
                    break
                v = rng.randint(1, m)
                clause.append(v if rng.random() < 0.5 else -v)
            clauses.append(clause)
        inst = {"num_vars": m, "clauses": clauses}
        Sat.validate(inst)
        # brute force
        expected = False
        for bits in itertools.product([False, True], repeat=m):
            if all(any((lit > 0) == bits[abs(lit) - 1] for lit in c) for c in clauses):
                expected = True
                break
        got = Sat.is_yes(inst)
        if expected != got:
            print("SAT MISMATCH", inst, expected, got)
            ok = False
        else:
            TESTS_PASSED += 1
    return ok


def test_problem_random_instances():
    ok = True
    rng = random.Random(2024)
    for scale in range(0, 13):
        for _ in range(200):
            inst = DominatingSet.random_instance(rng, scale)
            ok &= check(inst)
    return ok

def test_enumerate_instances():
    ok = True
    for inst in DominatingSet.enumerate_instances(4):
        ok &= check(inst)
    return ok


if __name__ == "__main__":
    results = []
    results.append(("exhaustive_small", test_exhaustive_small()))
    results.append(("random", test_random()))
    results.append(("target_random", test_target_random_instances()))
    results.append(("problem_random", test_problem_random_instances()))
    results.append(("enumerate", test_enumerate_instances()))
    for name, ok in results:
        print(f"{name}: {'PASS' if ok else 'FAIL'}")
    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    sys.exit(0 if all(ok for _, ok in results) else 1)
