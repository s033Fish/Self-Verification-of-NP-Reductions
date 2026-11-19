"""Tests comparing brute-force answers on small 3-SAT instances to their reductions."""
import itertools
import random

import problems
from reduce import reduce


def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any(bits[abs(l) - 1] == (l > 0) for l in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_dominating_set(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(0, k + 1):
        for combo in itertools.combinations(range(n), size):
            dom = set(combo)
            for v in combo:
                dom |= adj[v]
            if len(dom) == n:
                return True
    return False


def random_instance(rng, max_vars=4, max_clauses=4):
    m = rng.randint(0, max_vars)
    clauses = []
    if m >= 3:
        for _ in range(rng.randint(0, max_clauses)):
            vs = rng.sample(range(1, m + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    return {"num_vars": m, "clauses": clauses}


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    # Exhaustive-ish small cases plus random ones.
    cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 2, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
    ]
    for _ in range(400):
        cases.append(random_instance(rng))

    for inst in cases:
        problems.ThreeSat.validate(inst)
        red = reduce(inst)
        problems.DominatingSet.validate(red)
        a = solve_three_sat(inst)
        b = solve_dominating_set(red)
        tests_run += 1
        if a == b:
            tests_passed += 1
        else:
            print("MISMATCH", inst, red, a, b)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
