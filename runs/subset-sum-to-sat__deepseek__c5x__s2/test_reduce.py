"""Tests for the Subset Sum → SAT reduction.

The file contains a small test suite that generates random Subset Sum instances,
solves them by brute force, reduces them to SAT using ``reduce.reduce`` and
checks that the SAT instance has the same answer.
"""

from __future__ import annotations

import json
import random
import sys
from typing import List, Tuple

import problems
from reduce import reduce as reduction


def subset_sum_bruteforce(instance: dict) -> bool:
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]
    if target == 0:
        return True
    if target < 0:
        return False
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
        if s == target:
            return True
    return False


def sat_bruteforce(instance: dict) -> bool:
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for clause in clauses:
        if not clause:
            return False
    if not clauses:
        return True
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            sat = False
            for lit in clause:
                var = abs(lit)
                val = (mask >> (var - 1)) & 1
                if (lit > 0 and val) or (lit < 0 and not val):
                    sat = True
                    break
            if not sat:
                ok = False
                break
        if ok:
            return True
    return False


def generate_random_subset_sum(max_len: int = 5, max_val: int = 7) -> dict:
    length = random.randint(0, max_len)
    numbers = [random.randint(0, max_val) for _ in range(length)]
    target = random.randint(-max_val, max_val * length)
    return {"numbers": numbers, "target": target}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    failures: List[Tuple[dict, dict, bool, bool]] = []

    # Run a moderate number of random tests with small parameters.
    for _ in range(50):
        src = generate_random_subset_sum(max_len=2, max_val=2)
        problems.SubsetSum.validate(src)
        src_ans = subset_sum_bruteforce(src)
        sat_inst = reduction(src)
        problems.Sat.validate(sat_inst)
        sat_ans = sat_bruteforce(sat_inst)
        total += 1
        if src_ans == sat_ans:
            passed += 1
        else:
            failures.append((src, sat_inst, src_ans, sat_ans))

    # Hand‑crafted edge cases.
    edge_cases = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 5},
        {"numbers": [1, 2, 3], "target": -1},
        {"numbers": [0, 0], "target": 0},
        {"numbers": [0, 0], "target": 1},
    ]
    for src in edge_cases:
        problems.SubsetSum.validate(src)
        src_ans = subset_sum_bruteforce(src)
        sat_inst = reduction(src)
        problems.Sat.validate(sat_inst)
        sat_ans = sat_bruteforce(sat_inst)
        total += 1
        if src_ans == sat_ans:
            passed += 1
        else:
            failures.append((src, sat_inst, src_ans, sat_ans))

    verdict = {
        "verified": len(failures) == 0,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))
    if failures:
        print(f"\n{len(failures)} failures (showing first):", file=sys.stderr)
        for src, sat_inst, src_ans, sat_ans in failures[:3]:
            print("Source:", src, file=sys.stderr)
            print("SAT instance:", sat_inst, file=sys.stderr)
            print("src_ans", src_ans, "sat_ans", sat_ans, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
