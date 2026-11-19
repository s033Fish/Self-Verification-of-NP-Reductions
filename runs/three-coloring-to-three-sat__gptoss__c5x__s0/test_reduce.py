"""Independent tests for reduce.py (3-Coloring -> 3-SAT).

Solvers are written from the definitions in problems.py:

  * solve_coloring: exhaustive search over 3^n colourings.
  * solve_sat: complete DPLL with unit propagation.  DPLL is itself
    cross-checked against a pure 2^m brute force on many small random
    3-SAT formulas (see test_dpll_against_brute_force).

Then we compare the solvers' answers on many small source instances and
their reductions, and validate the produced target instances.
"""

from __future__ import annotations

import itertools
import random

from problems import ThreeColoring, ThreeSat
import reduce as reduce_module


# ----------------------------------------------------------------------
# Solvers

def solve_coloring(instance):
    """Brute force 3-colourability: try all 3^n colourings."""
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        if all(colouring[u] != colouring[v] for u, v in edges):
            return True
    return False


def _brute_force_sat(num_vars, clauses):
    """Try all 2^num_vars assignments (only for small num_vars)."""
    for bits in itertools.product((False, True), repeat=num_vars):
        if all(any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                   for l in c) for c in clauses):
            return True
    return False


def _dpll_sat(clauses):
    """Complete DPLL with unit propagation.  clauses: iterable of frozensets."""
    clauses = [frozenset(c) for c in clauses]
    # unit propagation
    while True:
        units = [next(iter(c)) for c in clauses if len(c) == 1]
        if not units:
            break
        u = units[0]
        new = []
        for c in clauses:
            if u in c:
                continue
            if -u in c:
                c2 = c - {-u}
                if not c2:
                    return False
                new.append(c2)
            else:
                new.append(c)
        clauses = new
    if not clauses:
        return True
    # pure literal elimination (optional, keeps it complete)
    lits = set()
    for c in clauses:
        lits |= c
    pure = [l for l in lits if -l not in lits]
    if pure:
        pset = set(pure)
        new = []
        for c in clauses:
            if c & pset:
                continue
            new.append(c)
        return _dpll_sat(new)
    # branch on a variable from the shortest clause
    shortest = min(clauses, key=len)
    v = abs(next(iter(shortest)))
    for val in (v, -v):
        new = []
        ok = True
        for c in clauses:
            if val in c:
                continue
            if -val in c:
                c2 = c - {-val}
                if not c2:
                    ok = False
                    break
                new.append(c2)
            else:
                new.append(c)
        if ok and _dpll_sat(new):
            return True
    return False


def solve_sat(instance):
    """Complete 3-SAT solver (DPLL)."""
    return _dpll_sat(instance["clauses"])


# ----------------------------------------------------------------------
# Test harness

tests_run = 0
tests_passed = 0
failures = []


def check(instance, label):
    global tests_run, tests_passed
    tests_run += 1
    try:
        target = reduce_module.reduce(instance)
        ThreeSat.validate(target)
        expected = solve_coloring(instance)
        got = solve_sat(target)
        if expected != got:
            failures.append((label, instance, target, expected, got))
            return False
        tests_passed += 1
        return True
    except Exception as exc:  # noqa: BLE001
        failures.append((label, instance, None, "exception", repr(exc)))
        return False


def all_graphs(n):
    """All simple graphs on n vertices (undirected, no loops)."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def test_dpll_against_brute_force():
    """Self-check the DPLL solver on random small 3-SAT formulas."""
    global tests_run, tests_passed
    rng = random.Random(999)
    for _ in range(1000):
        m = rng.randint(0, 9)
        k = rng.randint(0, 8)
        clauses = []
        for _ in range(k):
            if m < 3:
                break
            vs = rng.sample(range(1, m + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in vs])
        inst = {"num_vars": m, "clauses": clauses}
        ThreeSat.validate(inst)
        tests_run += 1
        a = _brute_force_sat(m, clauses)
        b = solve_sat(inst)
        if a != b:
            failures.append(("dpll-selftest", inst, None, a, b))
        else:
            tests_passed += 1


def main():
    random.seed(12345)

    # Self-check DPLL first.
    test_dpll_against_brute_force()

    # 1. Exhaustive over all graphs with n = 0..5.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g, f"exhaustive n={n}")

    # 2. Random larger graphs.
    for n in (7, 8, 9, 10):
        for _ in range(100):
            pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
            edges = [list(p) for p in pairs if random.random() < 0.5]
            check({"n": n, "edges": edges}, f"random n={n}")

    # 3. Specific edge cases from the definitions.
    check({"n": 0, "edges": []}, "n=0")
    check({"n": 1, "edges": []}, "n=1")
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, "K3")
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}, "K4")
    check({"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4],
                             [1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]}, "K5")
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]}, "C5")
    check({"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]]}, "C6")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:10]:
            print(f)

    import json
    verdict = {
        "verified": len(failures) == 0 and tests_run > 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("wrote verdict.json:", verdict)
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
