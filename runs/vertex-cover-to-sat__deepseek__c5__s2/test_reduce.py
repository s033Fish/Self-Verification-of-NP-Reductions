"""Independent tests for reduce.py (VertexCover -> Sat).

We implement our own solvers for both problems from the definitions in
problems.py, then compare answers on many small source instances and their
reductions.  We validate every produced target instance with
problems.Sat.validate, and check the reduction is fast (polynomial) on
larger inputs.
"""

from __future__ import annotations

import itertools
import json
import random
import time

from problems import VertexCover, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force Vertex Cover solver.

def vc_solve(instance: dict) -> bool:
    """Brute force: is there a vertex cover of size <= k?"""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(0, k + 1):
        for comb in itertools.combinations(range(n), size):
            chosen = set(comb)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


# ----------------------------------------------------------------------
# DPLL SAT solver with unit propagation (independent of reduce.py).

def sat_solve(instance: dict) -> bool:
    num_vars = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def propagate(clauses):
        """Unit propagation. Returns clause list, or None if unsat."""
        clauses = [list(c) for c in clauses]
        while True:
            unit = None
            for c in clauses:
                if len(c) == 0:
                    return None
                if len(c) == 1:
                    unit = c[0]
                    break
            if unit is None:
                return clauses
            new = []
            for c in clauses:
                if unit in c:
                    continue
                if -unit in c:
                    new.append([x for x in c if x != -unit])
                else:
                    new.append(c)
            clauses = new

    def solve(clauses):
        res = propagate(clauses)
        if res is None:
            return False
        clauses = res
        if not clauses:
            return True
        # Branch on a literal from the shortest clause.
        c = min(clauses, key=len)
        lit = c[0]
        for assume in (lit, -lit):
            new = [cl for cl in clauses if assume not in cl]
            new = [[x for x in cl if x != -assume] for cl in new]
            new.append([assume])
            if solve(new):
                return True
        return False

    return solve(clauses)


# ----------------------------------------------------------------------
# Test harness

TESTS_RUN = 0
TESTS_PASSED = 0
FAILURES: list[str] = []


def check(condition: bool, label: str) -> None:
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    if condition:
        TESTS_PASSED += 1
    else:
        FAILURES.append(label)


def check_instance(instance: dict, label: str) -> None:
    """Compare source answer with reduced answer, and validate the target."""
    VertexCover.validate(instance)
    source_ans = vc_solve(instance)
    target = reduce(instance)
    Sat.validate(target)  # must be a well-formed SAT instance
    target_ans = sat_solve(target)
    check(
        source_ans == target_ans,
        f"{label}: source={source_ans} target={target_ans} "
        f"instance={instance} target={target}",
    )


def all_graphs(n: int):
    """Yield every simple undirected graph on n vertices as edge lists."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if (mask >> i) & 1]
        yield edges


def main() -> None:
    random.seed(12345)

    # --- Exhaustive small graphs, every relevant k -------------------
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                inst = {"n": n, "edges": edges, "k": k}
                check_instance(inst, f"exhaustive n={n} k={k}")

    # --- Random small instances --------------------------------------
    for _ in range(300):
        n = random.randint(0, 7)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(e) for e in possible if random.random() < 0.4]
        k = random.randint(-1, n + 1)
        inst = {"n": n, "edges": edges, "k": k}
        check_instance(inst, f"random n={n} k={k}")

    # --- Random medium instances (DPLL handles these) ----------------
    for _ in range(60):
        n = random.randint(8, 10)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(e) for e in possible if random.random() < 0.35]
        k = random.randint(0, n)
        inst = {"n": n, "edges": edges, "k": k}
        check_instance(inst, f"medium n={n} k={k}")

    # --- Specific documented edge cases ------------------------------
    edge_cases = [
        {"n": 0, "edges": [], "k": -1},   # no graph, k<0 -> no
        {"n": 0, "edges": [], "k": 0},    # empty graph -> yes
        {"n": 3, "edges": [], "k": 0},    # no edges -> yes
        {"n": 3, "edges": [], "k": 5},    # no edges, k>=n -> yes
        {"n": 3, "edges": [[0, 1]], "k": 0},   # edge, k=0 -> no
        {"n": 3, "edges": [[0, 1]], "k": 1},   # edge, k=1 -> yes
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},  # two disjoint edges -> no
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},  # -> yes
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 3},  # k>=n -> yes
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 100},  # k>=n -> yes
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 1},
    ]
    for inst in edge_cases:
        check_instance(inst, f"edge-case {inst}")

    # --- Cardinality-only check: no edges, answer is just k >= 0 ------
    for n in range(0, 11):
        for k in range(-2, n + 3):
            inst = {"n": n, "edges": [], "k": k}
            check_instance(inst, f"no-edge n={n} k={k}")

    # --- Complete graph K5: cover needs >= 4 vertices ----------------
    edges = [[u, v] for u in range(5) for v in range(u + 1, 5)]
    check_instance({"n": 5, "edges": edges, "k": 3}, "K5 k=3")
    check_instance({"n": 5, "edges": edges, "k": 4}, "K5 k=4")

    # --- Reduction must be polynomial-time: large instances fast -----
    for n, k in [(200, 100), (500, 250), (1000, 500), (1000, 0), (1000, 1000)]:
        edges = [[i, i + 1] for i in range(n - 1)]
        inst = {"n": n, "edges": edges, "k": k}
        t0 = time.time()
        target = reduce(inst)
        dt = time.time() - t0
        Sat.validate(target)
        check(dt < 5.0, f"large n={n} k={k} took {dt:.3f}s")

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    if FAILURES:
        print("FAILURES:")
        for f in FAILURES[:20]:
            print("  ", f)

    verdict = {
        "verified": TESTS_RUN == TESTS_PASSED and TESTS_RUN > 0,
        "tests_run": TESTS_RUN,
        "tests_passed": TESTS_PASSED,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
