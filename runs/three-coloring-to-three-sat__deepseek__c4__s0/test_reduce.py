"""Tests for reduce.py: solvers + exhaustive/random small-instance checks."""

import itertools
import json
import random

import problems
from reduce import reduce


def solve_3col(inst):
    """Brute-force 3-colourability (small n)."""
    n = inst["n"]
    edges = inst["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        if all(colouring[u] != colouring[v] for u, v in edges):
            return True
    return False


def solve_3sat(inst):
    """DPLL-ish backtracking 3-SAT solver."""
    m = inst["num_vars"]
    clauses = [tuple(c) for c in inst["clauses"]]

    def rec(clauses, assign):
        # unit propagation
        while True:
            units = [c[0] for c in clauses if len(c) == 1]
            if not units:
                break
            lit = units[0]
            var = abs(lit)
            val = lit > 0
            if var in assign and assign[var] != val:
                return False
            assign[var] = val
            new = []
            for c in clauses:
                if lit in c:
                    continue
                c2 = tuple(l for l in c if l != -lit)
                if not c2:
                    return False
                new.append(c2)
            clauses = new
        if not clauses:
            return True
        # pick a literal from shortest clause
        shortest = min(clauses, key=len)
        lit = shortest[0]
        for val in (lit > 0, lit < 0):
            a2 = dict(assign)
            a2[abs(lit)] = val
            new = []
            ok = True
            for c in clauses:
                if (lit if val else -lit) in c:
                    continue
                c2 = tuple(l for l in c if l != (-lit if val else lit))
                if not c2:
                    ok = False
                    break
                new.append(c2)
            if ok and rec(new, a2):
                return True
        return False

    return rec(clauses, {})


def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def check(inst):
    problems.ThreeColoring.validate(inst)
    out = reduce(inst)
    problems.ThreeSat.validate(out)
    src = solve_3col(inst)
    tgt = solve_3sat(out)
    assert src == tgt, f"MISMATCH src={src} tgt={tgt} inst={inst} out={out}"
    return src


def main():
    tests_run = 0
    tests_passed = 0

    # Exhaustive over all graphs with n = 0..5.
    for n in range(0, 6):
        for inst in all_graphs(n):
            check(inst)
            tests_run += 1
            tests_passed += 1

    # Random larger graphs (n = 6..10) with various densities.
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(6, 10)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        p = rng.random()
        edges = [list(e) for e in pairs if rng.random() < p]
        inst = {"n": n, "edges": edges}
        check(inst)
        tests_run += 1
        tests_passed += 1

    # Explicit edge cases from the docstrings.
    for inst in [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},          # triangle: yes
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]]},  # K4: no
    ]:
        check(inst)
        tests_run += 1
        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, f)


if __name__ == "__main__":
    main()
