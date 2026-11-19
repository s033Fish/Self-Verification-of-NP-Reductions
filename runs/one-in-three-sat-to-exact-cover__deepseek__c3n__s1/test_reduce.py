"""Tests comparing brute-force answers on small 1-in-3-SAT instances with the
answers of their reductions to Exact Cover."""

from __future__ import annotations

import itertools
import random

from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def solve_one_in_three_sat(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            count = sum(1 for v in clause if bits[v - 1])
            if count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance: dict) -> bool:
    u = instance["universe_size"]
    sets = instance["sets"]
    full = (1 << u) - 1
    masks = []
    for s in sets:
        mask = 0
        for e in s:
            mask |= 1 << e
        masks.append(mask)

    # backtracking over the lowest uncovered element
    def rec(covered: int) -> bool:
        if covered == full:
            return True
        # lowest uncovered element
        e = 0
        while covered >> e & 1:
            e += 1
        for mask in masks:
            if mask >> e & 1 and (mask & covered) == 0:
                if rec(covered | mask):
                    return True
        return False

    return rec(0)


# ----------------------------------------------------------------------
# Instance generators

def all_clauses(m: int):
    return [list(c) for c in itertools.combinations(range(1, m + 1), 3)]


def small_source_instances():
    """All small 1-in-3-SAT instances (with repeats, up to a few clauses)."""
    # no-clause instances, including m = 0, 1, 2
    for m in range(0, 5):
        yield {"num_vars": m, "clauses": []}

    for m in range(3, 5):
        clauses = all_clauses(m)
        # all single-clause instances
        for c in clauses:
            yield {"num_vars": m, "clauses": [list(c)]}
        # all pairs of clauses (including repeated clauses)
        for c1 in clauses:
            for c2 in clauses:
                yield {"num_vars": m, "clauses": [list(c1), list(c2)]}
        # all triples of clauses
        for c1 in clauses:
            for c2 in clauses:
                for c3 in clauses:
                    yield {"num_vars": m, "clauses": [list(c1), list(c2), list(c3)]}


def random_source_instances(n: int, seed: int = 0):
    rng = random.Random(seed)
    for _ in range(n):
        m = rng.randint(3, 7)
        k = rng.randint(0, 8)
        clauses = []
        for _ in range(k):
            clauses.append(rng.sample(range(1, m + 1), 3))
        yield {"num_vars": m, "clauses": clauses}


# ----------------------------------------------------------------------
# Tests

def main() -> None:
    tests_run = 0
    tests_passed = 0

    instances = list(small_source_instances())
    instances += list(random_source_instances(400, seed=12345))
    instances += list(random_source_instances(400, seed=999))

    for src in instances:
        tests_run += 1
        expected = solve_one_in_three_sat(src)
        tgt = reduce(src)

        # structural sanity: the reduction output must be a valid Exact Cover
        assert set(tgt) == {"universe_size", "sets"}, tgt
        assert isinstance(tgt["universe_size"], int) and tgt["universe_size"] >= 0
        for s in tgt["sets"]:
            assert isinstance(s, list)
            assert len(set(s)) == len(s)
            for e in s:
                assert 0 <= e < tgt["universe_size"]

        got = solve_exact_cover(tgt)
        assert got == expected, (src, tgt, expected, got)
        tests_passed += 1

    # explicit edge-case checks
    edge_cases = [
        ({"num_vars": 0, "clauses": []}, True),
        ({"num_vars": 5, "clauses": []}, True),
        # (x1 or x2 or x3) alone: satisfiable
        ({"num_vars": 3, "clauses": [[1, 2, 3]]}, True),
        # clauses forcing contradiction: every clause must have exactly one true
        ({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]}, True),
        # variables 1,2,3 all forced true by separate clauses -> clause [1,2,3]
        # would have 3 true -> unsatisfiable
        (
            {
                "num_vars": 4,
                "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]],
            },
            False,
        ),
    ]
    for src, expected in edge_cases:
        tests_run += 1
        got = solve_exact_cover(reduce(src))
        assert got == expected, (src, expected, got)
        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    import json

    with open("verdict.json", "w") as f:
        json.dump(
            {"verified": True, "tests_run": tests_run, "tests_passed": tests_passed},
            f,
        )


if __name__ == "__main__":
    main()
