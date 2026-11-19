"""Independent tests for reduce.py: 3-Coloring -> SAT.

We use our own solvers (solvers.py) written from the definitions in
problems.py, and compare answers on many small source instances.
"""
import itertools
import random

from problems import ThreeColoring, Sat
from reduce import reduce
from solvers import solve_three_coloring_fast, solve_sat

tests_run = 0
tests_passed = 0


def check(instance, label=""):
    """Validate, reduce, and compare answers. Returns True iff all good."""
    global tests_run, tests_passed
    tests_run += 1
    try:
        ThreeColoring.validate(instance)
    except Exception as exc:
        print(f"FAIL[{label}] source invalid: {exc!r}")
        return False
    reduced = reduce(instance)
    try:
        Sat.validate(reduced)
    except Exception as exc:
        print(f"FAIL[{label}] reduced instance invalid: {exc!r} :: {reduced!r}")
        return False
    src = solve_three_coloring_fast(instance)
    tgt = solve_sat(reduced)
    if src != tgt:
        print(f"FAIL[{label}] mismatch: source={src} target={tgt}\n"
              f"  instance={instance!r}\n  reduced={reduced!r}")
        return False
    tests_passed += 1
    return True


def all_graphs(n):
    """All simple graphs on n labelled vertices."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def main():
    global tests_run, tests_passed
    # ---- Edge cases from the docstring --------------------------------
    check({"n": 0, "edges": []}, "n=0")
    for n in (1, 2, 3):
        for g in all_graphs(n):
            check(g, f"complete-enum n={n}")

    # ---- Exhaustive over all graphs on 4, 5 and 6 vertices ------------
    for n in (4, 5, 6):
        for g in all_graphs(n):
            check(g, f"complete-enum n={n}")

    # ---- Random larger graphs -----------------------------------------
    rng = random.Random(12345)
    for trial in range(500):
        n = rng.randint(0, 9)
        pairs = list(itertools.combinations(range(n), 2))
        p = rng.choice([0.15, 0.4, 0.7, 1.0])
        edges = [list(pp) for pp in pairs if rng.random() < p]
        check({"n": n, "edges": edges}, f"random trial={trial}")

    # ---- Explicit K4 and K5 are NO ------------------------------------
    k4 = {"n": 4, "edges": [[a, b] for a in range(4) for b in range(a + 1, 4)]}
    assert solve_three_coloring_fast(k4) is False
    check(k4, "K4")
    k5 = {"n": 5, "edges": [[a, b] for a in range(5) for b in range(a + 1, 5)]}
    assert solve_three_coloring_fast(k5) is False
    check(k5, "K5")

    # ---- Structural checks on the reduction ---------------------------
    for n in range(0, 6):
        r = reduce({"n": n, "edges": []})
        assert r["num_vars"] == 3 * n, r
        for clause in r["clauses"]:
            for lit in clause:
                assert lit != 0 and abs(lit) <= r["num_vars"], (lit, r)
    # Symmetric edges give semantically identical formulas (order-insensitive).
    def norm(r):
        return (r["num_vars"], sorted(tuple(sorted(c)) for c in r["clauses"]))
    a = reduce({"n": 3, "edges": [[0, 1], [1, 2]]})
    b = reduce({"n": 3, "edges": [[1, 0], [2, 1]]})
    assert norm(a) == norm(b), (a, b)
    tests_run += 1
    tests_passed += 1

    # ---- Polynomial size sanity (linear in n + |E|) -------------------
    for n in (10, 50, 200):
        edges = [[i, i + 1] for i in range(n - 1)]
        r = reduce({"n": n, "edges": edges})
        assert r["num_vars"] == 3 * n
        assert len(r["clauses"]) == 4 * n + 3 * len(edges), len(r["clauses"])
    tests_run += 1
    tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
