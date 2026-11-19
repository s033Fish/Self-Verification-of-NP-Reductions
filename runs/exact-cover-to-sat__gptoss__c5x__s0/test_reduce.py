"""Independent tests for reduce.py (Exact Cover -> SAT).

We implement brute-force solvers for both problems directly from the
definitions in problems.py, then compare the source answer with the
answer of the reduced target instance on many small instances.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import ExactCover, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions)
# ----------------------------------------------------------------------

def solve_exact_cover(instance: dict) -> bool:
    """True iff some sub-collection of sets partitions the universe."""
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    for mask in range(1 << n):
        covered = [0] * u
        for i in range(n):
            if (mask >> i) & 1:
                for e in sets[i]:
                    covered[e] += 1
        if all(c == 1 for c in covered):
            return True
    return False


def solve_sat(instance: dict) -> bool:
    """True iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            if not any(((mask >> (abs(lit) - 1)) & 1) == (lit > 0) for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------

TESTS_RUN = 0
TESTS_PASSED = 0
FAILURES = []


def check(instance: dict, label: str = "") -> None:
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    src = solve_exact_cover(instance)
    reduced = reduce(instance)
    # The reduction must produce a well-formed SAT instance.
    Sat.validate(reduced)
    tgt = solve_sat(reduced)
    if src == tgt:
        TESTS_PASSED += 1
    else:
        FAILURES.append((label, instance, src, reduced, tgt))
        print(f"MISMATCH {label}: instance={instance!r}")
        print(f"  source answer={src}, reduced={reduced!r}, target answer={tgt}")


def all_small_instances(max_u: int, max_sets: int):
    """Enumerate every instance with universe <= max_u and <= max_sets sets."""
    for u in range(max_u + 1):
        valid = []
        for r in range(u + 1):
            for comb in itertools.combinations(range(u), r):
                valid.append(list(comb))
        for nsets in range(max_sets + 1):
            for sets in itertools.product(valid, repeat=nsets):
                yield {"universe_size": u, "sets": [list(s) for s in sets]}


def random_instance(rng: random.Random, max_u: int, max_sets: int) -> dict:
    u = rng.randint(0, max_u)
    nsets = rng.randint(0, max_sets)
    sets = []
    for _ in range(nsets):
        size = rng.randint(0, u)
        sets.append(sorted(rng.sample(range(u), size)))
    return {"universe_size": u, "sets": sets}


def main() -> None:
    # 1. Hand-picked edge cases.
    edge_cases = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[], []]},
        {"universe_size": 1, "sets": []},
        {"universe_size": 1, "sets": [[]]},
        {"universe_size": 1, "sets": [[0]]},
        {"universe_size": 1, "sets": [[0], [0]]},
        {"universe_size": 2, "sets": [[0], [1]]},
        {"universe_size": 2, "sets": [[0, 1]]},
        {"universe_size": 2, "sets": [[0], [0, 1]]},
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2]]},
        {"universe_size": 3, "sets": [[0], [1], [2]]},
        {"universe_size": 3, "sets": [[0, 1, 2], [0]]},
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [0], [2]]},
        {"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 2], [1, 3]]},
    ]
    for inst in edge_cases:
        check(inst, "edge")

    # 2. Exhaustive enumeration: all instances with u<=3 and <=4 sets,
    #    and all with u<=4 and <=3 sets.
    for inst in all_small_instances(max_u=3, max_sets=4):
        check(inst, "exhaustive-u3")
    for inst in all_small_instances(max_u=4, max_sets=3):
        check(inst, "exhaustive-u4")

    # 3. Random instances.
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_instance(rng, max_u=6, max_sets=7), "random")

    # 4. Random instances with duplicated sets and empty sets emphasised.
    for _ in range(2000):
        u = rng.randint(0, 5)
        base = [sorted(rng.sample(range(u), rng.randint(0, u))) for _ in range(rng.randint(0, 4))]
        sets = [list(s) for s in base]
        for _ in range(rng.randint(0, 4)):
            if base:
                sets.append(list(rng.choice(base)))
            else:
                sets.append([])
        check({"universe_size": u, "sets": sets}, "dup/empty")

    # 5. Large-ish random instances (still solvable by brute force).
    for _ in range(200):
        check(random_instance(rng, max_u=10, max_sets=12), "large-random")

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert not FAILURES, "some tests failed"

    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": TESTS_RUN, "tests_passed": TESTS_PASSED}, f)


if __name__ == "__main__":
    main()
