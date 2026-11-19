"""Independent verification of reduce.py: NAE-3-SAT -> 3-Coloring.

We implement our own brute-force solvers directly from the problem
definitions in problems.py, then compare the source answer with the answer
of the reduced 3-Coloring instance on many small instances.
"""

from __future__ import annotations

import itertools
import random
import sys

from problems import NaeThreeSat, ThreeColoring
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers
# ----------------------------------------------------------------------

def nae3sat_solve(instance):
    """Return True iff the NAE-3-SAT instance is satisfiable."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=num_vars):
        ok = True
        for clause in clauses:
            values = []
            for lit in clause:
                var = abs(lit)
                val = bits[var - 1]
                values.append(val if lit > 0 else (not val))
            # not all equal: at least one True and at least one False
            if all(values) or not any(values):
                ok = False
                break
        if ok:
            return True
    return False


def three_coloring_solve(instance):
    """Return True iff the graph is 3-colourable (backtracking)."""
    n = instance["n"]
    edges = instance["edges"]
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    color = [-1] * n

    def backtrack(v):
        if v == n:
            return True
        # Try colours; symmetry breaking: first vertex fixed to 0 handled
        # naturally, but we still try all 3 for simplicity with pruning.
        for c in range(3):
            if all(color[w] != c for w in adj[v] if color[w] != -1):
                color[v] = c
                if backtrack(v + 1):
                    return True
                color[v] = -1
        return False

    # order vertices by degree for speed
    order = sorted(range(n), key=lambda x: -len(adj[x]))
    pos = [0] * n
    for i, v in enumerate(order):
        pos[v] = i
    color = [-1] * n

    def backtrack2(i):
        if i == n:
            return True
        v = order[i]
        for c in range(3):
            good = True
            for w in adj[v]:
                if pos[w] < i and color[w] == c:
                    good = False
                    break
            if good:
                color[v] = c
                if backtrack2(i + 1):
                    return True
                color[v] = -1
        return False

    return backtrack2(0)


# ----------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------

class Tester:
    def __init__(self):
        self.run = 0
        self.passed = 0
        self.failures = []

    def check(self, src, label=""):
        self.run += 1
        try:
            NaeThreeSat.validate(src)
        except Exception as exc:  # invalid generated instance -> our bug
            self.failures.append((label, src, "source invalid: %r" % (exc,)))
            return
        red = reduce(src)
        try:
            ThreeColoring.validate(red)
        except Exception as exc:
            self.failures.append((label, src, "reduced invalid: %r" % (exc,)))
            return
        want = nae3sat_solve(src)
        got = three_coloring_solve(red)
        if want == got:
            self.passed += 1
        else:
            self.failures.append(
                (label, src, "source=%s reduced=%s red=%r" % (want, got, red))
            )


def all_clauses(num_vars):
    """All distinct clauses (as sorted tuples) over the given variables."""
    result = []
    for vars3 in itertools.combinations(range(1, num_vars + 1), 3):
        for signs in itertools.product((1, -1), repeat=3):
            lits = [s * v for s, v in zip(signs, vars3)]
            result.append(tuple(sorted(lits, key=lambda x: (abs(x), x))))
    return result


def main():
    random.seed(12345)
    t = Tester()

    # --- Edge cases ---------------------------------------------------
    t.check({"num_vars": 0, "clauses": []}, "m=0 no clauses")
    for m in range(0, 5):
        t.check({"num_vars": m, "clauses": []}, "m=%d no clauses" % m)

    # --- Exhaustive over all clause subsets for m=3 -------------------
    cs3 = all_clauses(3)
    for r in range(len(cs3) + 1):
        for subset in itertools.combinations(cs3, r):
            t.check({"num_vars": 3, "clauses": [list(c) for c in subset]},
                    "m=3 subset")

    # --- Exhaustive over all clause subsets for m=4 (sampled) ---------
    cs4 = all_clauses(4)
    # all single clauses, all pairs, plus random larger subsets
    for c in cs4:
        t.check({"num_vars": 4, "clauses": [list(c)]}, "m=4 single")
    for c1, c2 in itertools.combinations(cs4, 2):
        t.check({"num_vars": 4, "clauses": [list(c1), list(c2)]}, "m=4 pair")
    for _ in range(2000):
        r = random.randint(0, 8)
        subset = random.sample(cs4, min(r, len(cs4)))
        t.check({"num_vars": 4, "clauses": [list(c) for c in subset]},
                "m=4 random")

    # --- Random instances for m = 1..7 --------------------------------
    for _ in range(3000):
        m = random.randint(1, 7)
        possible = all_clauses(m)
        if not possible:
            t.check({"num_vars": m, "clauses": []}, "small m")
            continue
        k = random.randint(0, min(8, len(possible)))
        subset = random.sample(possible, k)
        # occasionally duplicate clauses (allowed by definition)
        clauses = [list(c) for c in subset]
        if clauses and random.random() < 0.3:
            clauses.append(list(random.choice(clauses)))
        t.check({"num_vars": m, "clauses": clauses}, "random m=%d" % m)

    # --- Random instances with more variables -------------------------
    for _ in range(500):
        m = random.randint(8, 10)
        possible = all_clauses(m)
        k = random.randint(0, 6)
        subset = random.sample(possible, k)
        t.check({"num_vars": m, "clauses": [list(c) for c in subset]},
                "random m=%d" % m)

    print("tests_run =", t.run)
    print("tests_passed =", t.passed)
    if t.failures:
        print("FAILURES:", len(t.failures))
        for label, src, msg in t.failures[:10]:
            print("  ", label, src, "->", msg)
        sys.exit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
