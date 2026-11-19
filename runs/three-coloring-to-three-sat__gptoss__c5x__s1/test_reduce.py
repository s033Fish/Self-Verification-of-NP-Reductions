"""Independent verification of reduce.py (3-Coloring -> 3-SAT).

Writes verdict.json with the results.
"""
import itertools
import json
import random
import sys

from problems import ThreeColoring, ThreeSat
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Brute-force / exact solvers written from the problem definitions.
# ----------------------------------------------------------------------

def solve_3col(instance):
    """Exact 3-colorability solver by exhaustive search over 3^n colourings."""
    n = instance["n"]
    edges = instance["edges"]
    for assign in itertools.product(range(3), repeat=n):
        if all(assign[u] != assign[v] for (u, v) in edges):
            return True
    return False


def solve_3sat(instance):
    """Exact 3-SAT solver via DPLL with unit propagation."""
    num_vars = instance["num_vars"]
    clauses = [set(c) for c in instance["clauses"]]

    def rec(clauses):
        clauses = [set(c) for c in clauses]
        # unit propagation
        changed = True
        while changed:
            changed = False
            for c in clauses:
                if len(c) == 0:
                    return False
                if len(c) == 1:
                    lit = next(iter(c))
                    new = []
                    for cl in clauses:
                        if lit in cl:
                            continue
                        if -lit in cl:
                            cl = cl - {-lit}
                        new.append(cl)
                    clauses = new
                    changed = True
                    break
        if not clauses:
            return True
        # branch on a literal from a shortest clause
        c = min(clauses, key=len)
        lit = next(iter(c))
        for val in (True, False):
            chosen = lit if val else -lit
            new = []
            for cl in clauses:
                if chosen in cl:
                    continue
                cl2 = cl - ({-chosen})
                new.append(cl2)
            if rec(new):
                return True
        return False

    return rec(clauses)


# ----------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------

tests_run = 0
tests_passed = 0
failures = []


def check(source, label):
    global tests_run, tests_passed
    tests_run += 1
    try:
        ThreeColoring.validate(source)
        expected = solve_3col(source)
        target = reduce_mod.reduce(source)
        ThreeSat.validate(target)
        got = solve_3sat(target)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((label, source, expected, got))
    except Exception as exc:  # noqa: BLE001
        failures.append((label, source, "EXCEPTION", repr(exc)))


def all_graphs(n):
    verts = list(range(n))
    pairs = [(u, v) for u in verts for v in verts if u < v]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def main():
    # 1. Exhaustive over all simple graphs on 0..5 vertices.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g, f"exhaustive n={n}")

    # 2. Specific edge cases.
    check({"n": 0, "edges": []}, "n=0")
    check({"n": 1, "edges": []}, "n=1")
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, "triangle")
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}, "K4")
    # K4 plus isolated vertices
    check({"n": 6, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}, "K4+iso")
    # odd cycle C5 (not 3-colourable? C5 is 3-colourable yes)
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]}, "C5")
    # K5 (no)
    check({"n": 5, "edges": [[u, v] for u in range(5) for v in range(5) if u < v]}, "K5")

    # 3. Random graphs on 6..8 vertices.
    rng = random.Random(12345)
    for n in range(6, 9):
        for _ in range(300):
            pairs = [(u, v) for u in range(n) for v in range(n) if u < v]
            edges = [list(p) for p in pairs if rng.random() < 0.4]
            check({"n": n, "edges": edges}, f"random n={n}")

    # 4. Random sparse graphs (near colouring threshold).
    for n in range(6, 10):
        for _ in range(200):
            pairs = [(u, v) for u in range(n) for v in range(n) if u < v]
            k = rng.randint(0, len(pairs))
            edges = [list(p) for p in rng.sample(pairs, k)]
            check({"n": n, "edges": edges}, f"random-sparse n={n}")

    # 5. Structural checks on reduce output.
    structural_ok = True
    for n in range(0, 7):
        for g in all_graphs(n):
            t = reduce_mod.reduce(g)
            if set(t) != {"num_vars", "clauses"}:
                structural_ok = False
            for c in t["clauses"]:
                if len(c) != 3 or len({abs(l) for l in c}) != 3:
                    structural_ok = False
                if any(l == 0 for l in c):
                    structural_ok = False
            if any(abs(l) > t["num_vars"] for c in t["clauses"] for l in c):
                structural_ok = False
    if not structural_ok:
        failures.append(("structural", None, None, None))

    verdict = {
        "verified": len(failures) == 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print(json.dumps(verdict))
    if failures:
        print("FAILURES (first 10):")
        for f in failures[:10]:
            print(f)
        sys.exit(1)


if __name__ == "__main__":
    main()
