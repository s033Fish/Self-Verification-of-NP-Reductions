"""Independent tests for reduce.py (NAE-3-SAT -> 3-Coloring).

We implement our own exact solvers for both problems from the definitions in
problems.py, generate many small source instances, reduce each one, and check
that the source answer equals the target answer.  We also check that the
reduced instance is a valid ThreeColoring instance and that its size is
polynomial in the input size.
"""

import itertools
import random
import time

from problems import NaeThreeSat, ThreeColoring
from reduce import reduce


# ----------------------------------------------------------------------
# Exact solvers (written from the problem definitions)

def nae_sat_solve(instance):
    """Brute force over all 2^m assignments."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << m):
        # value[v] is True iff bit (v-1) of mask is set
        value = [False] * (m + 1)
        for v in range(1, m + 1):
            value[v] = bool((mask >> (v - 1)) & 1)
        good = True
        for clause in clauses:
            lits = []
            for lit in clause:
                lits.append(value[abs(lit)] if lit > 0 else not value[abs(lit)])
            if all(lits) or not any(lits):
                good = False
                break
        if good:
            return True
    return False


def three_color_solve(instance):
    """Exact backtracking 3-colouring."""
    n = instance["n"]
    edges = instance["edges"]
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    color = [-1] * n
    # colour the most constrained vertices first
    order = sorted(range(n), key=lambda x: -len(adj[x]))

    def bt(i):
        if i == n:
            return True
        v = order[i]
        used = {color[u] for u in adj[v] if color[u] != -1}
        for c in range(3):
            if c not in used:
                color[v] = c
                if bt(i + 1):
                    return True
                color[v] = -1
        return False

    return bt(0)


# ----------------------------------------------------------------------
# Instance generation

def all_valid_clauses(m):
    """All clauses with 3 literals on 3 distinct variables from 1..m."""
    clauses = []
    for vars_ in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product((1, -1), repeat=3):
            clauses.append([s * v for s, v in zip(signs, vars_)])
    return clauses


def make_instance(m, clauses):
    return {"num_vars": m, "clauses": [list(c) for c in clauses]}


def random_instance(rng, max_m=5, max_k=5):
    m = rng.randint(0, max_m)
    if m < 3:
        clauses = []
    else:
        clauses = []
        for _ in range(rng.randint(0, max_k)):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
    return make_instance(m, clauses)


# ----------------------------------------------------------------------
# Test harness

class Harness:
    def __init__(self):
        self.run = 0
        self.passed = 0
        self.failures = []

    def check(self, instance, label=""):
        self.run += 1
        try:
            NaeThreeSat.validate(instance)
        except Exception as exc:  # invalid generated instance -> our bug
            self.failures.append((label, "source invalid: %r" % (exc,), instance))
            return
        expected = nae_sat_solve(instance)
        reduced = reduce(instance)
        # reduced must be a valid target instance
        ThreeColoring.validate(reduced)
        got = three_color_solve(reduced)
        if got != expected:
            self.failures.append(
                (label, "expected %s got %s" % (expected, got), instance)
            )
            return
        self.passed += 1


def main():
    h = Harness()
    rng = random.Random(12345)

    # --- edge cases: no clauses, small m (including m = 0) ---------------
    for m in range(0, 7):
        h.check(make_instance(m, []), "no-clauses m=%d" % m)

    # --- exhaustive over all clause subsets for m = 3 -------------------
    base_clauses = all_valid_clauses(3)  # 8 clauses
    for r in range(len(base_clauses) + 1):
        for combo in itertools.combinations(base_clauses, r):
            h.check(make_instance(3, combo), "exhaustive m=3 r=%d" % r)

    # --- exhaustive-ish for m = 4: all single clauses and pairs ----------
    clauses4 = all_valid_clauses(4)  # 32 clauses
    for c in clauses4:
        h.check(make_instance(4, [c]), "m=4 single")
    for c1, c2 in itertools.combinations(clauses4, 2):
        h.check(make_instance(4, [c1, c2]), "m=4 pair")

    # --- duplicates of clauses ------------------------------------------
    for c in clauses4[:10]:
        h.check(make_instance(4, [c, c, c]), "m=4 triple-dup")

    # --- random instances -----------------------------------------------
    for _ in range(400):
        h.check(random_instance(rng, max_m=5, max_k=5), "random")

    # --- random instances with more clauses -----------------------------
    for _ in range(100):
        h.check(random_instance(rng, max_m=4, max_k=8), "random-dense")

    # --- polynomial-size sanity check -----------------------------------
    for m, k in [(1, 0), (3, 1), (5, 5), (10, 20), (50, 100)]:
        clauses = []
        for i in range(k):
            vs = [(i % m) + 1, ((i + 1) % m) + 1, ((i + 2) % m) + 1]
            if len(set(vs)) == 3:
                clauses.append(vs)
        inst = make_instance(m, clauses)
        red = reduce(inst)
        # n = 3 + 2m + 3k at most; edges likewise linear
        assert red["n"] <= 3 + 2 * m + 3 * k, (m, k, red["n"])
        assert len(red["edges"]) <= 3 + 3 * m + 6 * k, (m, k, len(red["edges"]))
        h.run += 1
        h.passed += 1

    print("tests_run=%d tests_passed=%d" % (h.run, h.passed))
    for label, msg, inst in h.failures[:20]:
        print("FAIL", label, msg, inst)
    if h.failures:
        print("TOTAL FAILURES:", len(h.failures))

    import json
    verdict = {
        "verified": len(h.failures) == 0 and h.run == h.passed,
        "tests_run": h.run,
        "tests_passed": h.passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)
    return h


if __name__ == "__main__":
    t0 = time.time()
    main()
    print("elapsed %.2fs" % (time.time() - t0))
