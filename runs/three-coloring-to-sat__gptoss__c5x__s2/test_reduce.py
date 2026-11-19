"""Independent tests for reduce.py (3-Coloring -> SAT).

We implement our own brute-force solvers for both problems from the
definitions in problems.py, then compare answers on many small source
instances and their reductions.  We also check that the reduction output
is a valid SAT instance and that reduce runs in polynomial time.
"""

from __future__ import annotations

import itertools
import json
import random
import time

from problems import ThreeColoring, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_three_coloring(instance: dict) -> bool:
    """True iff the graph is 3-colourable (backtracking, degree order)."""
    n = instance["n"]
    adj = [set() for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].add(v)
        adj[v].add(u)
    order = sorted(range(n), key=lambda v: -len(adj[v]))
    colour = {}

    def rec(i: int) -> bool:
        if i == n:
            return True
        v = order[i]
        used = {colour[u] for u in adj[v] if u in colour}
        for c in range(3):
            if c not in used:
                colour[v] = c
                if rec(i + 1):
                    return True
                del colour[v]
        return False

    return rec(0)


def solve_sat(instance: dict) -> bool:
    """True iff the CNF formula is satisfiable (DPLL with unit propagation)."""
    clauses = [list(c) for c in instance["clauses"]]

    def rec(clauses, assignment):
        new = []
        for cl in clauses:
            satisfied = False
            remaining = []
            for lit in cl:
                val = assignment.get(abs(lit))
                if val is None:
                    remaining.append(lit)
                elif (lit > 0) == val:
                    satisfied = True
                    break
            if satisfied:
                continue
            if not remaining:
                return False
            new.append(remaining)
        if not new:
            return True
        for cl in new:
            if len(cl) == 1:
                lit = cl[0]
                a = dict(assignment)
                a[abs(lit)] = lit > 0
                return rec(new, a)
        lit = new[0][0]
        for val in (lit > 0, lit < 0):
            a = dict(assignment)
            a[abs(lit)] = val
            if rec(new, a):
                return True
        return False

    return rec(clauses, {})


# ----------------------------------------------------------------------
# Test harness

tests_run = 0
tests_passed = 0
failures = []


def check(condition: bool, message: str) -> None:
    global tests_run, tests_passed
    tests_run += 1
    if condition:
        tests_passed += 1
    else:
        failures.append(message)


def check_instance(graph: dict, label: str) -> None:
    """Compare source answer with reduced target answer; validate output."""
    ThreeColoring.validate(graph)
    src = solve_three_coloring(graph)
    sat = reduce(graph)
    Sat.validate(sat)  # must be a valid SAT instance
    check(True, f"{label}: output valid")
    tgt = solve_sat(sat)
    check(src == tgt, f"{label}: source={src} target={tgt} graph={graph}")


def all_graphs(n: int):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield {"n": n, "edges": [list(p) for i, p in enumerate(pairs) if mask & (1 << i)]}


def main() -> None:
    # Exhaustive over all graphs with 0..5 vertices (1100 graphs).
    for n in range(0, 6):
        for graph in all_graphs(n):
            check_instance(graph, f"exhaustive n={n}")

    # Specific edge cases from the docstrings.
    check_instance({"n": 0, "edges": []}, "edge n=0")
    check_instance({"n": 1, "edges": []}, "edge n=1")
    check_instance({"n": 2, "edges": [[0, 1]]}, "edge n=2")
    check_instance({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, "edge n=3 triangle")
    for k in (4, 5, 6):
        edges = [list(p) for p in itertools.combinations(range(k), 2)]
        check_instance({"n": k, "edges": edges}, f"edge K{k}")

    rng = random.Random(12345)

    # Random graphs with 6 and 7 vertices.
    for n in (6, 7):
        pairs = list(itertools.combinations(range(n), 2))
        for _ in range(300):
            edges = [list(p) for p in pairs if rng.random() < 0.5]
            check_instance({"n": n, "edges": edges}, f"random n={n}")

    # Larger graphs that are guaranteed 3-colourable: pick a random
    # 3-colouring and only add edges between differently coloured vertices.
    for n in (8, 15, 30, 60):
        for _ in range(15):
            colours = [rng.randrange(3) for _ in range(n)]
            edges = []
            seen = set()
            for _ in range(3 * n):
                u = rng.randrange(n)
                v = rng.randrange(n)
                if u == v or colours[u] == colours[v]:
                    continue
                key = frozenset((u, v))
                if key not in seen:
                    seen.add(key)
                    edges.append([u, v])
            check_instance({"n": n, "edges": edges}, f"colorable n={n}")

    # Larger graphs that are guaranteed NOT 3-colourable: K4 plus extras.
    for extra in (0, 1, 5, 20):
        n = 4 + extra
        edges = [list(p) for p in itertools.combinations(range(4), 2)]
        for v in range(4, n):
            edges.append([v, 0])
        check_instance({"n": n, "edges": edges}, f"non-colorable K4+{extra}")

    # Reduction must run in polynomial time: time a large instance.
    n = 1000
    edges = [[i, i + 1] for i in range(n - 1)]
    start = time.time()
    sat = reduce({"n": n, "edges": edges})
    elapsed = time.time() - start
    check(elapsed < 5.0, f"reduce too slow on n={n}: {elapsed:.3f}s")
    check(sat["num_vars"] == 3 * n, "variable count is 3n")
    Sat.validate(sat)
    check(True, "large output valid")

    verdict = {
        "verified": len(failures) == 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh, indent=2)
        fh.write("\n")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for msg in failures[:20]:
            print("  " + msg)
    else:
        print("ALL TESTS PASSED")
    print(json.dumps(verdict))


if __name__ == "__main__":
    main()
