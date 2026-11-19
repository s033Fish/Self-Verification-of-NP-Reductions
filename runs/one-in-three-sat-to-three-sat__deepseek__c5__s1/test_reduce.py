"""Independent tests for reduce.py: 1-in-3-SAT -> 3-SAT.

We implement our own brute-force / DPLL solvers from the problem
definitions in problems.py (which has no solvers) and compare answers
on many small source instances and their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import OneInThreeSat, ThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers (written from the definitions, independent of reduce.py)


def solve_one_in_three(instance):
    """Brute force: exactly one true variable in every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for (a, b, c) in clauses:
            # variables are 1..m
            count = int(bits[a - 1]) + int(bits[b - 1]) + int(bits[c - 1])
            if count != 1:
                ok = False
                break
        if ok:
            return True
    return True if not clauses else False


def solve_three_sat(instance):
    """DPLL solver: every clause has at least one true literal."""
    n = instance["num_vars"]
    clauses = [tuple(c) for c in instance["clauses"]]

    def propagate(clauses, assign):
        """Return simplified clause list, or None on conflict."""
        clauses = list(clauses)
        changed = True
        while changed:
            changed = False
            new_clauses = []
            for cl in clauses:
                satisfied = False
                unassigned = []
                for lit in cl:
                    v = abs(lit)
                    if v in assign:
                        val = assign[v]
                        if (lit > 0) == val:
                            satisfied = True
                            break
                    else:
                        unassigned.append(lit)
                if satisfied:
                    continue
                if not unassigned:
                    return None  # empty clause -> conflict
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    v = abs(lit)
                    val = lit > 0
                    if v in assign:
                        if assign[v] != val:
                            return None
                    else:
                        assign[v] = val
                        changed = True
                        continue
                new_clauses.append(unassigned)
            clauses = new_clauses
        return clauses

    def solve(clauses, assign):
        res = propagate(clauses, assign)
        if res is None:
            return False
        if not res:
            return True
        lit = res[0][0]
        v = abs(lit)
        for val in (True, False):
            a2 = dict(assign)
            a2[v] = val
            if solve(res, a2):
                return True
        return False

    return solve(clauses, {})


# ----------------------------------------------------------------------
# Test helpers


def check(instance, results):
    """Validate, solve source, reduce, validate target, compare."""
    OneInThreeSat.validate(instance)
    src = solve_one_in_three(instance)
    target = reduce(instance)
    ThreeSat.validate(target)
    tgt = solve_three_sat(target)
    results["run"] += 1
    if src == tgt:
        results["passed"] += 1
    else:
        results["failures"].append((instance, target, src, tgt))


def random_source(rng, max_vars=6, max_clauses=5):
    m = rng.randint(0, max_vars)
    clauses = []
    if m >= 3:
        nclauses = rng.randint(0, max_clauses)
        for _ in range(nclauses):
            vs = rng.sample(range(1, m + 1), 3)
            rng.shuffle(vs)
            clauses.append(vs)
    return {"num_vars": m, "clauses": clauses}


def main():
    results = {"run": 0, "passed": 0, "failures": []}

    # --- Explicit edge cases -----------------------------------------
    edge = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
        {"num_vars": 5, "clauses": [[1, 2, 3], [3, 4, 5], [1, 4, 5]]},
    ]
    for inst in edge:
        check(inst, results)

    # --- Exhaustive-ish: all single clauses and pairs for m=3,4 ------
    for m in (3, 4):
        all_clauses = [list(c) for c in itertools.combinations(range(1, m + 1), 3)]
        for c in all_clauses:
            check({"num_vars": m, "clauses": [c]}, results)
        for c1 in all_clauses:
            for c2 in all_clauses:
                check({"num_vars": m, "clauses": [c1, c2]}, results)

    # --- Random instances --------------------------------------------
    rng = random.Random(12345)
    for _ in range(4000):
        check(random_source(rng), results)

    print(f"tests_run={results['run']} tests_passed={results['passed']}")
    if results["failures"]:
        print("FAILURES:")
        for inst, target, src, tgt in results["failures"][:5]:
            print("  source:", inst, "src_ans=", src)
            print("  target:", target, "tgt_ans=", tgt)
    return results


if __name__ == "__main__":
    main()
