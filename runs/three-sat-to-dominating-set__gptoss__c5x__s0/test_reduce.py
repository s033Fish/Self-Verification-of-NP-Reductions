"""Independent tests for reduce.py: 3-SAT -> Dominating Set.

Solvers are written directly from the definitions in problems.py (no
solvers are provided there).  We compare the source answer with the answer
of the reduced target instance on many small instances, including an
exhaustive family and explicit edge cases.
"""
import itertools
import random

from reduce import reduce


# ----------------------------------------------------------------------
# Solvers (from the problem definitions)
# ----------------------------------------------------------------------

def sat_solve(instance):
    """True iff the 3-CNF formula is satisfiable (brute force over 2^m)."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assign in itertools.product([False, True], repeat=m):
        good = True
        for clause in clauses:
            if not any(
                (assign[abs(lit) - 1] if lit > 0 else not assign[abs(lit) - 1])
                for lit in clause
            ):
                good = False
                break
        if good:
            return True
    return False


def min_dominating_set_size(instance):
    """Exact minimum dominating set size (branch and bound)."""
    n = instance["n"]
    adj = [0] * n
    for u, v in instance["edges"]:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    closed = [adj[v] | (1 << v) for v in range(n)]
    best = n

    def rec(dominated, chosen):
        nonlocal best
        if chosen >= best:
            return
        if dominated == (1 << n) - 1:
            best = chosen
            return
        und = [v for v in range(n) if not (dominated >> v) & 1]
        v = max(und, key=lambda x: bin(closed[x]).count("1"))
        options = [v] + [w for w in range(n) if (adj[v] >> w) & 1]
        for cand in options:
            rec(dominated | closed[cand], chosen + 1)

    rec(0, 0)
    return best


def dominating_set_solve(instance):
    """True iff there is a dominating set of size at most k."""
    k = instance["k"]
    n = instance["n"]
    if k < 0:
        return False
    if k >= n:
        return True
    return min_dominating_set_size(instance) <= k


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_clauses(m):
    """All 3-literal clauses on 3 distinct variables over vars 1..m."""
    clauses = []
    for combo in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            clauses.append([s * v for s, v in zip(signs, combo)])
    return clauses


def random_instance(rng, m, max_clauses):
    allc = all_clauses(m)
    if not allc:
        return {"num_vars": m, "clauses": []}
    count = rng.randint(0, min(max_clauses, len(allc)))
    return {"num_vars": m, "clauses": [list(c) for c in rng.sample(allc, count)]}


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

def check(instance, label, failures, counter):
    counter[0] += 1
    expected = sat_solve(instance)
    reduced = reduce(instance)
    got = dominating_set_solve(reduced)
    if expected != got:
        failures.append((label, instance, reduced, expected, got))
    return expected == got


def main():
    rng = random.Random(12345)
    failures = []
    counter = [0]

    # 1. Exhaustive over all formulas for m = 0, 1, 2, 3.
    for m in range(0, 4):
        allc = all_clauses(m)
        for mask in range(1 << len(allc)):
            clauses = [list(allc[i]) for i in range(len(allc)) if mask >> i & 1]
            check({"num_vars": m, "clauses": clauses},
                  f"exhaustive m={m} mask={mask}", failures, counter)

    # 2. Random instances for m = 3..6.
    for m in range(3, 7):
        for _ in range(120):
            check(random_instance(rng, m, 12), f"random m={m}", failures, counter)

    # 3. Hand-picked edge cases (including the known counterexample).
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]},
        {"num_vars": 3, "clauses": all_clauses(3)},  # unsat
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
        # Minimal counterexample found during review: unsatisfiable, but the
        # reduction has a dominating set of size k = m + 1.
        {"num_vars": 4, "clauses": [
            [-1, 3, -4], [-1, -2, -4], [1, 3, -4], [1, -3, -4], [1, 2, 4],
            [-1, 3, 4], [-1, 2, -3], [-2, -3, 4], [-2, 3, 4]]},
    ]
    for inst in edge_cases:
        check(inst, f"edge {inst}", failures, counter)

    print(f"tests_run={counter[0]} failures={len(failures)}")
    for label, inst, reduced, expected, got in failures[:5]:
        print("FAIL", label, "expected", expected, "got", got)
        print("  source:", inst)
        print("  reduced n,k:", reduced["n"], reduced["k"])

    return len(failures) == 0, counter[0], len(failures)


if __name__ == "__main__":
    ok, total, nfail = main()
    print("ALL_OK" if ok else "FAILURES_FOUND")
