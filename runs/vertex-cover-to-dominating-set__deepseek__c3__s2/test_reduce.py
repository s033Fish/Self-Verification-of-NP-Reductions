"""Tests for the Vertex Cover -> Dominating Set reduction."""

import random

import problems
from problems import SOURCE, TARGET
from reduce import reduce


def check(instance, stats):
    stats["run"] += 1
    # The reduction must produce a valid target instance.
    out = reduce(instance)
    TARGET.validate(out)
    src = SOURCE.is_yes(instance)
    dst = TARGET.is_yes(out)
    stats["passed" if src == dst else "failed"] += 1
    if src != dst:
        print("MISMATCH")
        print("  source:", instance, "->", src)
        print("  target:", out, "->", dst)
    return src == dst


def main():
    stats = {"run": 0, "passed": 0, "failed": 0}

    # 1. Exhaustive over all graphs up to 4 vertices with k from -1 to n+1.
    for instance in SOURCE.enumerate_instances(4):
        check(instance, stats)
    print("after exhaustive scale 4:", stats)

    # 2. Exhaustive over all graphs up to 5 vertices (bigger).
    for instance in SOURCE.enumerate_instances(5):
        check(instance, stats)
    print("after exhaustive scale 5:", stats)

    # 3. Random instances at several scales.
    rng = random.Random(12345)
    for scale in range(0, 9):
        for _ in range(120):
            check(SOURCE.random_instance(rng, scale), stats)
    print("after random:", stats)

    # 4. Hand-picked edge cases.
    hand = [
        {"n": 0, "edges": [], "k": -1},
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 5},
        {"n": 5, "edges": [], "k": -1},
        {"n": 5, "edges": [], "k": 0},
        {"n": 5, "edges": [], "k": 3},
        {"n": 5, "edges": [], "k": 100},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 3},
        {"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 2},
        {"n": 1, "edges": [], "k": -5},
        {"n": 1, "edges": [], "k": 0},
    ]
    for instance in hand:
        check(instance, stats)
    print("after hand-picked:", stats)

    print("TOTAL run=%d passed=%d failed=%d" % (stats["run"], stats["passed"], stats["failed"]))
    import json
    verdict = {
        "verified": stats["failed"] == 0 and stats["run"] == stats["passed"],
        "tests_run": stats["run"],
        "tests_passed": stats["passed"],
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("wrote verdict.json:", verdict)
    return stats


if __name__ == "__main__":
    s = main()
    assert s["failed"] == 0, "some tests failed"
    print("ALL TESTS PASSED")
