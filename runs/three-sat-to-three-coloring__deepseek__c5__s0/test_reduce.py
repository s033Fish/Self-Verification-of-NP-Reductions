"""Independent tests for reduce.py: 3-SAT (ThreeSat) -> 3-Coloring (ThreeColoring).

We implement brute-force solvers for both problems from the definitions in
problems.py, then compare the source answer with the answer of the reduced
target instance on many small source instances.

The reduction is checked for:
  * validity of every produced target instance,
  * agreement of source and target answers (soundness AND completeness),
  * polynomial size (implicitly: n and edges are linear in the input size).
"""

from __future__ import annotations

import itertools
import json
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers, written from the problem definitions.

def sat_solve(instance: dict) -> bool:
    """True iff some assignment of vars 1..m satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        if all(
            any(((bits >> (abs(lit) - 1)) & 1) == (lit > 0) for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def coloring_solve(instance: dict) -> bool:
    """True iff the graph is 3-colourable (backtracking)."""
    n = instance["n"]
    adj = [[] for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].append(v)
        adj[v].append(u)
    color = [-1] * n

    def bt(i: int) -> bool:
        if i == n:
            return True
        for c in range(3):
            if all(color[j] != c for j in adj[i] if color[j] != -1):
                color[i] = c
                if bt(i + 1):
                    return True
                color[i] = -1
        return False

    return bt(0)


def coloring_solve_bruteforce(instance: dict) -> bool:
    """Independent O(3^n) reference solver (used only for tiny graphs)."""
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    for assignment in itertools.product(range(3), repeat=n):
        if all(assignment[u] != assignment[v] for u, v in edges):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation.

def random_sat(rng: random.Random) -> dict:
    m = rng.randint(0, 4)
    n_clauses = 0 if m < 3 else rng.randint(0, 6)
    clauses = []
    for _ in range(n_clauses):
        vs = rng.sample(range(1, m + 1), 3)
        clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    return {"num_vars": m, "clauses": clauses}


def forcing_counterexample() -> dict:
    """Satisfiable formula where clause (1 or 2 or 3) is all-true in every
    satisfying assignment (x,y,z are each forced true by four clauses over
    two fresh auxiliary variables)."""
    clauses = []
    for forced, a, b in ((1, 4, 5), (2, 6, 7), (3, 8, 9)):
        clauses += [
            [forced, a, b], [forced, -a, b],
            [forced, a, -b], [forced, -a, -b],
        ]
    clauses.append([1, 2, 3])
    return {"num_vars": 9, "clauses": clauses}


def all_true_clause_counterexample() -> dict:
    """Even smaller: (1 or 2 or 3) plus clauses forcing all of 1,2,3 true."""
    return forcing_counterexample()


# ----------------------------------------------------------------------
# Main test driver.

def main() -> None:
    rng = random.Random(12345)

    tests_run = 0
    tests_passed = 0
    failures = []

    # --- 0. Cross-check the colouring solver against brute force on tiny graphs.
    solver_checks = 0
    for _ in range(300):
        n = rng.randint(0, 7)
        all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        rng.shuffle(all_edges)
        k = rng.randint(0, len(all_edges))
        g = {"n": n, "edges": [list(e) for e in all_edges[:k]]}
        problems.ThreeColoring.validate(g)
        assert coloring_solve(g) == coloring_solve_bruteforce(g)
        solver_checks += 1
    print(f"colouring solver cross-checks passed: {solver_checks}")

    # --- 1. Build the source instance suite.
    instances = [random_sat(rng) for _ in range(600)]
    instances += [
        # Edge cases from the definitions.
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 2, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3], [-1, 2, 3], [1, -2, 3], [1, 2, -3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, -3], [1, 2, -4]]},
        # Explicit counterexamples: satisfiable, but a clause is all-true.
        forcing_counterexample(),
    ]

    # --- 2. Compare source and reduced answers.
    for inst in instances:
        problems.ThreeSat.validate(inst)
        src = sat_solve(inst)
        red = reduce(inst)
        problems.ThreeColoring.validate(red)
        tgt = coloring_solve(red)
        tests_run += 1
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, src, red, tgt))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for inst, src, red, tgt in failures[:5]:
        print("MISMATCH: source answer", src, "target answer", tgt)
        print("  source:", inst)
        print("  target n:", red["n"], "edges:", len(red["edges"]))

    # --- 3. The known counterexample must fail (reduction is incomplete).
    ce = forcing_counterexample()
    ce_src = sat_solve(ce)
    ce_tgt = coloring_solve(reduce(ce))
    print("forcing counterexample: source =", ce_src, ", target =", ce_tgt)
    assert ce_src is True and ce_tgt is False, "expected counterexample to fail"

    verified = len(failures) == 0
    verdict = {
        "verified": verified,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
