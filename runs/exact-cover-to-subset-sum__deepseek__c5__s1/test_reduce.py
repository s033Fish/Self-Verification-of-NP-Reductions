"""Independent verification of reduce.py (Exact Cover -> Subset Sum).

Writes verdict.json with {"verified", "tests_run", "tests_passed"}.
"""
import itertools
import json
import random

from problems import ExactCover, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def brute_exact_cover(inst):
    """Yes iff some sub-collection of sets is pairwise disjoint and covers 0..u-1."""
    u = inst["universe_size"]
    sets = inst["sets"]
    m = len(sets)
    universe = set(range(u))
    for mask in range(1 << m):
        seen = set()
        ok = True
        for i in range(m):
            if (mask >> i) & 1:
                for e in sets[i]:
                    if e in seen:          # not pairwise disjoint
                        ok = False
                        break
                    seen.add(e)
                if not ok:
                    break
        if ok and seen == universe:
            return True
    return False


def brute_subset_sum(inst):
    """Yes iff some sub-list sums exactly to target (each position at most once)."""
    t = inst["target"]
    if t < 0:
        return False
    reachable = {0}
    for a in inst["numbers"]:
        reachable |= {x + a for x in reachable}
    return t in reachable


# ----------------------------------------------------------------------

def main():
    results = {"tests_run": 0, "tests_passed": 0, "failures": []}

    def check(inst):
        ExactCover.validate(inst)
        out = reduce(inst)
        SubsetSum.validate(out)
        a = brute_exact_cover(inst)
        b = brute_subset_sum(out)
        results["tests_run"] += 1
        if a == b:
            results["tests_passed"] += 1
        else:
            results["failures"].append(
                {"instance": inst, "reduced": out, "source": a, "target": b}
            )

    # 1) Explicit edge cases.
    edge_cases = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[], [], []]},
        {"universe_size": 1, "sets": []},
        {"universe_size": 1, "sets": [[]]},
        {"universe_size": 1, "sets": [[0]]},
        {"universe_size": 1, "sets": [[0], [0]]},
        {"universe_size": 2, "sets": [[0], [1]]},
        {"universe_size": 2, "sets": [[0, 1]]},
        {"universe_size": 2, "sets": [[0], [0], [1]]},
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2]]},
        {"universe_size": 3, "sets": [[0, 1, 2], [0], [1], [2]]},
        {"universe_size": 3, "sets": [[], [0, 1, 2], [], [0, 1, 2]]},
        {"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 2], [1, 3]]},
    ]
    for inst in edge_cases:
        check(inst)

    # 2) Exhaustive small instances: all lists of m subsets of a u-element universe.
    for u in range(0, 4):
        all_subsets = []
        for r in range(u + 1):
            all_subsets.extend(list(c) for c in itertools.combinations(range(u), r))
        for m in range(0, 4):
            for combo in itertools.product(all_subsets, repeat=m):
                check({"universe_size": u, "sets": [list(s) for s in combo]})

    # 3) Random small instances (including duplicates and empty sets).
    rng = random.Random(12345)
    for _ in range(4000):
        u = rng.randint(0, 6)
        m = rng.randint(0, 8)
        sets = []
        for _ in range(m):
            k = rng.randint(0, u)
            sets.append(sorted(rng.sample(range(u), k)))
        check({"universe_size": u, "sets": sets})

    # 4) Structured instances: partition-style (guaranteed yes) and near-misses.
    for u in range(0, 7):
        if u == 0:
            check({"universe_size": 0, "sets": []})
            continue
        # a genuine partition into singletons
        check({"universe_size": u, "sets": [[e] for e in range(u)]})
        # one big set plus singletons
        check({"universe_size": u, "sets": [list(range(u))] + [[e] for e in range(u)]})
        # all pairs
        pairs = [list(c) for c in itertools.combinations(range(u), 2)]
        check({"universe_size": u, "sets": pairs})
        # duplicates of a covering set
        check({"universe_size": u, "sets": [list(range(u)), list(range(u))]})
        # missing element
        if u >= 1:
            check({"universe_size": u, "sets": [list(range(u - 1))]})

    verified = results["tests_passed"] == results["tests_run"] and not results["failures"]
    verdict = {
        "verified": bool(verified),
        "tests_run": results["tests_run"],
        "tests_passed": results["tests_passed"],
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)

    print("tests_run   =", results["tests_run"])
    print("tests_passed=", results["tests_passed"])
    print("failures    =", len(results["failures"]))
    for fail in results["failures"][:5]:
        print("FAIL:", fail)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
