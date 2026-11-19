"""Independent tests for reduce.py (Exact Cover -> Subset Sum).

We implement our own brute-force solvers straight from the docstrings in
problems.py, generate many small source instances, reduce them, and compare
the solvers' answers.  We also check that every reduction output is a valid
SubsetSum instance and that reduce() does not blow up in time.
"""

from __future__ import annotations

import itertools
import random
import time

from problems import ExactCover, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def exact_cover_brute(instance: dict) -> bool:
    """Yes iff some sub-collection of sets is pairwise disjoint with union
    equal to the whole universe."""
    u = instance["universe_size"]
    sets = instance["sets"]
    full = (1 << u) - 1
    m = len(sets)
    masks = []
    for s in sets:
        mask = 0
        for e in s:
            mask |= 1 << e
        masks.append(mask)
    # Enumerate every sub-list of sets.
    for bits in range(1 << m):
        union = 0
        ok = True
        for i in range(m):
            if (bits >> i) & 1:
                if union & masks[i]:
                    ok = False
                    break
                union |= masks[i]
        if ok and union == full:
            return True
    return False


def subset_sum_brute(instance: dict) -> bool:
    """Yes iff some sub-list of numbers sums exactly to target."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for a in numbers:
        # a is non-negative; each position used at most once.
        reachable = reachable | {s + a for s in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Instance generation.

def random_source_instance(rng: random.Random) -> dict:
    u = rng.randint(0, 5)
    m = rng.randint(0, 6)
    sets = []
    for _ in range(m):
        # Random subset of 0..u-1 (possibly empty).
        s = [e for e in range(u) if rng.random() < 0.5]
        sets.append(s)
    # Occasionally duplicate an existing set to exercise the duplicate rule.
    if sets and rng.random() < 0.3:
        sets.append(list(rng.choice(sets)))
    return {"universe_size": u, "sets": sets}


def structured_instances() -> list[dict]:
    out = []
    # u = 0 with various set collections.
    out.append({"universe_size": 0, "sets": []})
    out.append({"universe_size": 0, "sets": [[], []]})
    # no sets.
    out.append({"universe_size": 3, "sets": []})
    # exact cover exists.
    out.append({"universe_size": 3, "sets": [[0, 1], [2]]})
    # exact cover needs two disjoint sets.
    out.append({"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 2]]})
    # duplicate non-empty set (cannot both be chosen).
    out.append({"universe_size": 2, "sets": [[0], [0], [1]]})
    # duplicate of a covering set.
    out.append({"universe_size": 2, "sets": [[0, 1], [0, 1]]})
    # empty sets never matter.
    out.append({"universe_size": 2, "sets": [[], [0], [], [1], []]})
    # overlapping sets only.
    out.append({"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2]]})
    # single set covering everything.
    out.append({"universe_size": 3, "sets": [[0, 1, 2]]})
    # element missing entirely.
    out.append({"universe_size": 3, "sets": [[0, 1]]})
    # many copies of the same set.
    out.append({"universe_size": 2, "sets": [[0]] * 4 + [[1]] * 4})
    return out


# ----------------------------------------------------------------------
# Test driver.

def main() -> int:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance: dict, label: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        # Input must be a valid source instance.
        try:
            ExactCover.validate(instance)
        except Exception as exc:  # pragma: no cover - generator bug
            failures.append((label, instance, f"source invalid: {exc}"))
            return
        reduced = reduce(instance)
        # Output must be a valid target instance.
        try:
            SubsetSum.validate(reduced)
        except Exception as exc:
            failures.append((label, instance, f"target invalid: {exc}", reduced))
            return
        want = exact_cover_brute(instance)
        got = subset_sum_brute(reduced)
        if want == got:
            tests_passed += 1
        else:
            failures.append((label, instance, f"expected {want}, got {got}", reduced))

    # Structured edge cases.
    for idx, inst in enumerate(structured_instances()):
        check(inst, f"structured[{idx}]")

    # Exhaustive small instances: u in 0..3, all collections of up to 3 sets
    # drawn from all subsets of the universe (with repetition allowed).
    for u in range(0, 4):
        all_subsets = []
        for r in range(u + 1):
            for combo in itertools.combinations(range(u), r):
                all_subsets.append(list(combo))
        for m in range(0, 4):
            for choice in itertools.product(all_subsets, repeat=m):
                inst = {"universe_size": u, "sets": [list(c) for c in choice]}
                check(inst, f"exhaustive u={u} m={m}")

    # Random instances.
    for i in range(3000):
        check(random_source_instance(rng), f"random[{i}]")

    # Slightly larger random instances (still brute-forceable).
    for i in range(300):
        u = rng.randint(0, 8)
        m = rng.randint(0, 10)
        sets = []
        for _ in range(m):
            s = [e for e in range(u) if rng.random() < 0.4]
            sets.append(s)
        check({"universe_size": u, "sets": sets}, f"large[{i}]")

    # Timing sanity check on a moderately sized instance (polynomial claim).
    big_u = 200
    big_sets = []
    for i in range(300):
        # random-ish sets
        big_sets.append([(i + j) % big_u for j in range(5)])
    t0 = time.time()
    out = reduce({"universe_size": big_u, "sets": big_sets})
    dt = time.time() - t0
    SubsetSum.validate(out)
    print(f"timing: reduce on u={big_u}, m={len(big_sets)} took {dt:.4f}s")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:20]:
            print("  ", f)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
