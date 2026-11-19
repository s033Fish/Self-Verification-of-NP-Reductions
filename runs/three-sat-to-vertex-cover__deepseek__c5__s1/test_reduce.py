"""Independent brute-force solvers and tests for the 3-SAT -> Vertex Cover reduction.

We implement our own solvers from the problem definitions (problems.py has none),
generate many small source instances (including explicitly unsatisfiable ones),
reduce each with reduce.reduce, and compare the answers.
"""
import itertools
import json
import random

from problems import ThreeSat, VertexCover
import reduce as reduce_module


# ---------------------------------------------------------------- solvers
def solve_three_sat(instance):
    """Brute force over all assignments of variables 1..num_vars."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                       for l in clause):
                ok = False
                break
        if ok:
            return True
    return False


def min_vertex_cover_size(edges):
    """Exact minimum vertex cover size via branching + memoization."""
    edges = frozenset(frozenset(e) for e in edges)
    memo = {}

    def rec(rem):
        if not rem:
            return 0
        if rem in memo:
            return memo[rem]
        u, v = next(iter(rem))
        rem_u = frozenset(e for e in rem if u not in e)
        rem_v = frozenset(e for e in rem if v not in e)
        best = 1 + min(rec(rem_u), rec(rem_v))
        memo[rem] = best
        return best

    return rec(edges)


def solve_vertex_cover(instance):
    """Brute force: is there a vertex cover of size <= k?"""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if not edges:
        return k >= 0
    if k >= n:
        return True
    return min_vertex_cover_size(edges) <= k


# ---------------------------------------------------------------- generators
def all_clauses_over(variables):
    """All 3-literal clauses over 3 distinct variables from the given list."""
    out = []
    for vars_ in itertools.combinations(sorted(variables), 3):
        for signs in itertools.product([1, -1], repeat=3):
            out.append([s * v for s, v in zip(signs, vars_)])
    return out


def random_three_sat(rng, max_vars=3, max_clauses=4):
    m = rng.randint(0, max_vars)
    clauses = []
    if m >= 3:
        pool = all_clauses_over(range(1, m + 1))
        for _ in range(rng.randint(0, max_clauses)):
            clauses.append(list(rng.choice(pool)))
    return {"num_vars": m, "clauses": clauses}


def unsat_instances():
    """Explicitly unsatisfiable formulas: all 8 clauses over a 3-var subset."""
    out = []
    # minimal unsat over exactly 3 vars
    out.append({"num_vars": 3, "clauses": all_clauses_over([1, 2, 3])})
    # embedded in larger variable sets (extra vars unused)
    out.append({"num_vars": 4, "clauses": all_clauses_over([1, 2, 3])})
    out.append({"num_vars": 5, "clauses": all_clauses_over([3, 4, 5])})
    out.append({"num_vars": 6, "clauses": all_clauses_over([2, 4, 6])})
    return out


def enumerate_small_instances():
    instances = []
    for m in range(0, 4):
        instances.append({"num_vars": m, "clauses": []})
    pool3 = all_clauses_over([1, 2, 3])  # 8 clauses over 3 vars
    for c in pool3:
        instances.append({"num_vars": 3, "clauses": [list(c)]})
    for c1 in pool3:
        for c2 in pool3:
            instances.append({"num_vars": 3, "clauses": [list(c1), list(c2)]})
    instances.append({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    instances.extend(unsat_instances())
    return instances


def main():
    rng = random.Random(12345)
    instances = enumerate_small_instances()
    for _ in range(600):
        instances.append(random_three_sat(rng))

    tests_run = 0
    tests_passed = 0
    failures = []

    for inst in instances:
        try:
            ThreeSat.validate(inst)
        except Exception as e:  # pragma: no cover
            failures.append(("invalid source", inst, repr(e)))
            continue

        reduced = reduce_module.reduce(inst)
        tests_run += 1
        try:
            VertexCover.validate(reduced)
        except Exception as e:
            failures.append(("invalid target", inst, repr(e)))
            continue

        src = solve_three_sat(inst)
        tgt = solve_vertex_cover(reduced)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append(("mismatch", inst,
                             {"source": src, "target": tgt}))

    result = {
        "tests_run": tests_run,
        "tests_passed": tests_passed,
        "num_failures": len(failures),
        "sample_failures": [
            {"kind": k, "instance": i, "detail": d} for k, i, d in failures[:5]
        ],
    }
    print(json.dumps(result, indent=2, default=str))
    return result


if __name__ == "__main__":
    main()
