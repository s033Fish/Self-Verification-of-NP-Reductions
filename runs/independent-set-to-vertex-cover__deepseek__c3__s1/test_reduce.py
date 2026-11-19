import random

import problems
from problems import IndependentSet, VertexCover
from reduce import reduce


def test_many_random():
    rng = random.Random(12345)
    tests = 0
    passed = 0
    for scale in range(1, 7):
        for _ in range(400):
            inst = IndependentSet.random_instance(rng, scale)
            IndependentSet.validate(inst)
            red = reduce(inst)
            VertexCover.validate(red)
            src = IndependentSet.is_yes(inst)
            tgt = VertexCover.is_yes(red)
            tests += 1
            if src == tgt:
                passed += 1
            else:
                raise AssertionError(
                    "mismatch: %r -> %r (src=%s tgt=%s)" % (inst, red, src, tgt)
                )
    return tests, passed


def test_exhaustive_small():
    tests = 0
    passed = 0
    for scale in range(1, 5):
        for inst in IndependentSet.enumerate_instances(scale):
            IndependentSet.validate(inst)
            red = reduce(inst)
            VertexCover.validate(red)
            src = IndependentSet.is_yes(inst)
            tgt = VertexCover.is_yes(red)
            tests += 1
            if src == tgt:
                passed += 1
            else:
                raise AssertionError(
                    "mismatch: %r -> %r (src=%s tgt=%s)" % (inst, red, src, tgt)
                )
    return tests, passed


def test_edge_cases():
    tests = 0
    passed = 0
    cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 1},
        {"n": 0, "edges": [], "k": -5},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": 3},
        {"n": 3, "edges": [], "k": 4},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": -1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 5},
        {"n": 5, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 5, "edges": [[0, 1], [2, 3]], "k": 3},
        {"n": 5, "edges": [[0, 1], [2, 3]], "k": 4},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 0},
    ]
    for inst in cases:
        IndependentSet.validate(inst)
        red = reduce(inst)
        VertexCover.validate(red)
        src = IndependentSet.is_yes(inst)
        tgt = VertexCover.is_yes(red)
        tests += 1
        if src == tgt:
            passed += 1
        else:
            raise AssertionError(
                "mismatch: %r -> %r (src=%s tgt=%s)" % (inst, red, src, tgt)
            )
    return tests, passed


if __name__ == "__main__":
    total = 0
    ok = 0
    for fn in (test_exhaustive_small, test_edge_cases, test_many_random):
        t, p = fn()
        print("%s: %d/%d" % (fn.__name__, p, t))
        total += t
        ok += p
    print("TOTAL: %d/%d" % (ok, total))
    assert ok == total
