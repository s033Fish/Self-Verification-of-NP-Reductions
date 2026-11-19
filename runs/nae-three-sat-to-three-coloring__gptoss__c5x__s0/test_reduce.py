"""Independent tests for reduce.py (NAE-3-SAT -> 3-Coloring).

We implement our own brute-force solvers from the problem definitions in
problems.py (which has no solvers), generate many small source instances,
reduce them, and compare answers.
"""

from __future__ import annotations

import itertools
import json
import random
import sys

from problems import NaeThreeSat, ThreeColoring
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.

def brute_nae(instance):
    """Return True iff the NAE-3-SAT instance is satisfiable (not-all-equal)."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << m):
        good = True
        for clause in clauses:
            vals = []
            for lit in clause:
                v = abs(lit)
                val = (mask >> (v - 1)) & 1
                if lit < 0:
                    val = 1 - val
                vals.append(val)
            # not all equal
            if all(vals) or not any(vals):
                good = False
                break
        if good:
            return True
    return False


def brute_3col(instance):
    """Return True iff the graph is 3-colourable (backtracking)."""
    n = instance["n"]
    edges = instance["edges"]
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    colors = [-1] * n
    order = sorted(range(n), key=lambda x: -len(adj[x]))

    def bt(idx):
        if idx == n:
            return True
        v = order[idx]
        used = {colors[u] for u in adj[v] if colors[u] != -1}
        for c in range(3):
            if c not in used:
                colors[v] = c
                if bt(idx + 1):
                    return True
                colors[v] = -1
        return False

    return bt(0)


# ----------------------------------------------------------------------
# Instance generators (all valid by construction).

def rand_nae(rng, max_vars=5, max_clauses=6):
    m = rng.randint(0, max_vars)
    if m < 3:
        n_clauses = 0
    else:
        n_clauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(n_clauses):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_nae_with_vars(m, max_clauses):
    """Yield all NAE instances over exactly m vars with up to max_clauses clauses."""
    if m < 3:
        yield {"num_vars": m, "clauses": []}
        return
    # all possible clauses over m vars (ordered literals, but order irrelevant)
    possible = []
    for combo in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product((1, -1), repeat=3):
            possible.append([s * v for s, v in zip(signs, combo)])
    for k in range(0, max_clauses + 1):
        for chosen in itertools.combinations(possible, k):
            yield {"num_vars": m, "clauses": [list(c) for c in chosen]}


# ----------------------------------------------------------------------
# Test harness.

class Harness:
    def __init__(self):
        self.run = 0
        self.passed = 0
        self.failures = []

    def check(self, instance, label):
        self.run += 1
        try:
            NaeThreeSat.validate(instance)
        except Exception as exc:  # pragma: no cover
            self.failures.append((label, "source invalid: %r" % (exc,), instance))
            return
        expected = brute_nae(instance)
        try:
            out = reduce(instance)
        except Exception as exc:
            self.failures.append((label, "reduce raised %r" % (exc,), instance))
            return
        try:
            ThreeColoring.validate(out)
        except Exception as exc:
            self.failures.append((label, "target invalid: %r" % (exc,), (instance, out)))
            return
        got = brute_3col(out)
        if got != expected:
            self.failures.append(
                (label, "mismatch expected=%s got=%s" % (expected, got), (instance, out))
            )
            return
        self.passed += 1


def main():
    h = Harness()

    # 1. Explicit edge cases.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]},
        {"num_vars": 4, "clauses": [[1, -2, 3], [-1, 2, -3], [4, 1, 2]]},
        {"num_vars": 5, "clauses": [[1, 2, 3], [-1, -2, -3], [1, 2, 4],
                                    [-1, -2, -4], [3, 4, 5], [-3, -4, -5]]},
    ]
    for i, inst in enumerate(edge_cases):
        h.check(inst, "edge_case_%d" % i)

    # 2. Exhaustive over small variable counts.
    for m in (0, 1, 2, 3, 4):
        for inst in all_nae_with_vars(m, max_clauses=3):
            h.check(inst, "exhaustive_m%d" % m)

    # 3. Randomised testing.
    rng = random.Random(12345)
    for _ in range(4000):
        inst = rand_nae(rng, max_vars=6, max_clauses=7)
        h.check(inst, "random")

    # 4. Larger random instances (still brute-forceable).
    for _ in range(300):
        inst = rand_nae(rng, max_vars=8, max_clauses=8)
        h.check(inst, "random_large")


    # 5. Polynomial-time / large-instance sanity check (no brute force).
    import time
    rng2 = random.Random(999)
    big = {"num_vars": 200, "clauses": []}
    for _ in range(400):
        vs = rng2.sample(range(1, 201), 3)
        big["clauses"].append([v if rng2.random() < 0.5 else -v for v in vs])
    t0 = time.time()
    out_big = reduce(big)
    elapsed = time.time() - t0
    h.run += 1
    ok = True
    try:
        ThreeColoring.validate(out_big)
    except Exception as exc:
        ok = False
        h.failures.append(("large", "target invalid: %r" % (exc,), out_big))
    if out_big["n"] != 1 + 2 * 200 + 3 * 400:
        ok = False
        h.failures.append(("large", "wrong n=%d" % out_big["n"], out_big["n"]))
    if elapsed > 5.0:
        ok = False
        h.failures.append(("large", "too slow: %.3fs" % elapsed, elapsed))
    if ok:
        h.passed += 1

    verified = (len(h.failures) == 0)
    verdict = {
        "verified": verified,
        "tests_run": h.run,
        "tests_passed": h.passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
        fh.write("\n")

    print("tests_run=%d tests_passed=%d failures=%d"
          % (h.run, h.passed, len(h.failures)))
    for label, msg, data in h.failures[:10]:
        print("FAIL", label, msg)
        print("  ", data)
    print("verdict:", verdict)
    return 0 if verified else 1


if __name__ == "__main__":
    sys.exit(main())
