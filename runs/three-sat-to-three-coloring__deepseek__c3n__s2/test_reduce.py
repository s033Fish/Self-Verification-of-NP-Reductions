"""Tests for reduce.py: compare brute-force solvers on small instances."""

import itertools
import random
import sys

sys.path.insert(0, ".")
from problems import ThreeSat, ThreeColoring  # noqa: E402
from reduce import reduce  # noqa: E402


def solve_3sat(instance):
    """Brute force 3-SAT over all 2^m assignments."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << m):
        good = True
        for clause in clauses:
            sat = False
            for lit in clause:
                v = abs(lit)
                val = (mask >> (v - 1)) & 1
                if (lit > 0 and val == 1) or (lit < 0 and val == 0):
                    sat = True
                    break
            if not sat:
                good = False
                break
        if good:
            return True
    return False


def solve_3col(instance):
    """Backtracking 3-colouring with an MRV-style vertex choice."""
    n = instance["n"]
    adj = [set() for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].add(v)
        adj[v].add(u)
    color = [-1] * n

    def bt():
        best = -1
        best_deg = -1
        for i in range(n):
            if color[i] == -1:
                d = sum(1 for j in adj[i] if color[j] != -1)
                if d > best_deg:
                    best_deg = d
                    best = i
        if best == -1:
            return True
        used = {color[j] for j in adj[best] if color[j] != -1}
        for c in range(3):
            if c not in used:
                color[best] = c
                if bt():
                    return True
                color[best] = -1
        return False

    return bt()


TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance, label=""):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    ThreeSat.validate(instance)
    reduced = reduce(instance)
    ThreeColoring.validate(reduced)
    a = solve_3sat(instance)
    b = solve_3col(reduced)
    if a == b:
        TESTS_PASSED += 1
        return True
    print(f"FAIL {label}: sat={a} col={b} instance={instance}")
    return False


def main():
    # Specific edge cases.
    check({"num_vars": 0, "clauses": []}, "m=0 no clauses")
    check({"num_vars": 3, "clauses": []}, "m=3 no clauses")
    check({"num_vars": 5, "clauses": []}, "m=5 no clauses")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}, "two clauses")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clause")
    check({"num_vars": 4, "clauses": [[1, 2, 3]]}, "unused var")
    check({"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 4]]}, "mixed")

    all_clauses = []
    for signs in itertools.product([1, -1], repeat=3):
        all_clauses.append([signs[i] * (i + 1) for i in range(3)])
    check({"num_vars": 3, "clauses": all_clauses}, "unsat all 8 clauses")

    rng = random.Random(12345)
    for _ in range(400):
        m = rng.randint(0, 4)
        clauses = []
        if m >= 3:
            nc = rng.randint(0, 3)
            for _ in range(nc):
                vs = rng.sample(range(1, m + 1), 3)
                clause = [v if rng.random() < 0.5 else -v for v in vs]
                clauses.append(clause)
        check({"num_vars": m, "clauses": clauses}, "random")

    # A few larger random instances.
    for _ in range(40):
        m = rng.randint(5, 6)
        nc = rng.randint(1, 4)
        clauses = []
        for _ in range(nc):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
        check({"num_vars": m, "clauses": clauses}, "larger random")

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    if TESTS_PASSED != TESTS_RUN:
        sys.exit(1)


if __name__ == "__main__":
    main()
