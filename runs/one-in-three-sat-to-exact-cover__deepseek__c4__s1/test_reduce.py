"""Brute-force solvers and randomized/exhaustive tests for the reduction."""

import itertools
import random

import problems
from reduce import reduce


# ------------------------- brute-force solvers -------------------------

def solve_one_in_three_sat(instance):
    """Brute force over all assignments of variables 1..m."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            cnt = sum(1 for v in clause if bits[v - 1])
            if cnt != 1:
                ok = False
                break
        if ok:
            return True
    return True if not clauses else False


def solve_exact_cover(instance):
    """Brute force over subsets of sets (small instances only)."""
    u = instance["universe_size"]
    sets = instance["sets"]
    full = (1 << u) - 1
    n = len(sets)
    # iterate over subsets of set-indices
    for r in range(n + 1):
        for combo in itertools.combinations(range(n), r):
            covered = 0
            good = True
            for idx in combo:
                mask = 0
                for e in sets[idx]:
                    mask |= 1 << e
                if covered & mask:
                    good = False
                    break
                covered |= mask
            if good and covered == full:
                return True
    return False


# ------------------------- exhaustive small source instances -----------

def all_source_instances(max_vars=4, max_clauses=3):
    """Yield small valid 1-in-3-SAT instances."""
    for m in range(0, max_vars + 1):
        if m < 3:
            clause_choices = [None]  # only empty clause list possible
        else:
            clause_choices = list(itertools.combinations(range(1, m + 1), 3))
        if m < 3:
            yield {"num_vars": m, "clauses": []}
            continue
        # subsets of clauses up to max_clauses (allow duplicates separately)
        for r in range(0, max_clauses + 1):
            for combo in itertools.combinations(clause_choices, r):
                yield {"num_vars": m, "clauses": [list(c) for c in combo]}


def random_source_instance(rng):
    m = rng.randint(0, 6)
    if m < 3:
        return {"num_vars": m, "clauses": []}
    k = rng.randint(0, 6)
    clauses = []
    for _ in range(k):
        clauses.append(list(rng.sample(range(1, m + 1), 3)))
    return {"num_vars": m, "clauses": clauses}


def check(instance, results):
    problems.OneInThreeSat.validate(instance)
    target = reduce(instance)
    problems.ExactCover.validate(target)
    a = solve_one_in_three_sat(instance)
    b = solve_exact_cover(target)
    results["run"] += 1
    if a == b:
        results["passed"] += 1
    else:
        results["failures"].append((instance, target, a, b))


def main():
    results = {"run": 0, "passed": 0, "failures": []}

    # exhaustive small
    for inst in all_source_instances(max_vars=4, max_clauses=3):
        check(inst, results)

    # random
    rng = random.Random(12345)
    for _ in range(400):
        check(random_source_instance(rng), results)

    # explicit edge cases
    edges = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [2, 3, 4]]},
        {"num_vars": 6, "clauses": [[1, 2, 3], [4, 5, 6]]},
        {"num_vars": 3, "clauses": [[1, 2, 3]] * 4},
    ]
    for inst in edges:
        check(inst, results)


    # larger random stress
    rng2 = random.Random(999)
    for _ in range(300):
        m = rng2.randint(0, 8)
        if m < 3:
            inst = {"num_vars": m, "clauses": []}
        else:
            k = rng2.randint(0, 10)
            inst = {"num_vars": m,
                    "clauses": [list(rng2.sample(range(1, m + 1), 3)) for _ in range(k)]}
        check(inst, results)

    print(f"run={results['run']} passed={results['passed']}")
    for f in results["failures"][:5]:
        print("FAILURE:", f)
    assert not results["failures"], "some tests failed"
    print("ALL TESTS PASSED")
    return results


if __name__ == "__main__":
    main()
