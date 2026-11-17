"""Tests for the 3-SAT -> Exact Cover reduction in reduce.py.

Compares problems.SOURCE.is_yes on small 3-SAT instances with
problems.TARGET.is_yes on their reductions, and validates the outputs.
"""

from __future__ import annotations

import random
import sys

import problems
from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    """Reduce, validate, and compare both brute-force answers."""
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    assert got == expected, (
        f"mismatch for {instance!r}: 3-SAT={expected}, ExactCover={got}, "
        f"reduced={reduced!r}"
    )
    tests_passed += 1


def test_enumerated():
    """Every 3-SAT instance with num_vars <= 3 (distinct clauses)."""
    for instance in SOURCE.enumerate_instances(SOURCE.exhaustive_scale):
        check(instance)


def test_random():
    """Random instances at several scales, both satisfiable and not."""
    rng = random.Random(12345)
    for scale in range(0, 8):
        for _ in range(60):
            check(SOURCE.random_instance(rng, scale))


def test_handmade_edge_cases():
    # no clauses, m = 0
    check({"num_vars": 0, "clauses": []})
    # no clauses, m > 0
    check({"num_vars": 5, "clauses": []})
    # all 8 clauses on 3 vars: unsatisfiable
    clauses = [
        [a, b, c]
        for a in (1, -1)
        for b in (2, -2)
        for c in (3, -3)
    ]
    check({"num_vars": 3, "clauses": clauses})
    # all but one clause: satisfiable
    check({"num_vars": 3, "clauses": clauses[:-1]})
    # repeated clauses
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]})
    # unused variables mixed in
    check({"num_vars": 6, "clauses": [[1, 2, 3], [-1, -2, -3]]})
    # single clause
    check({"num_vars": 3, "clauses": [[1, -2, 3]]})
    # duplicate-literal-free but tricky
    check({"num_vars": 4, "clauses": [[1, 2, 3], [-1, 2, 4], [1, -2, -4], [-3, 4, -1]]})


def test_structure():
    """The reduction output has the expected shape and is polynomial."""
    inst = {"num_vars": 4, "clauses": [[1, 2, 3], [-1, 2, 4]]}
    out = reduce(inst)
    assert out["universe_size"] == 4 + 4 * 2
    # 2 sets per variable + 2 sets per clause-literal
    assert len(out["sets"]) == 2 * 4 + 2 * 3 * 2
    for s in out["sets"]:
        assert len(set(s)) == len(s)
        for e in s:
            assert 0 <= e < out["universe_size"]



def test_stress():
    """Extra random cross-check across seeds and scales."""
    for seed in range(5):
        rng = random.Random(1000 + seed)
        for scale in range(0, 7):
            for _ in range(20):
                check(SOURCE.random_instance(rng, scale))

if __name__ == "__main__":
    test_structure()
    test_handmade_edge_cases()
    test_enumerated()
    test_random()
    test_stress()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
