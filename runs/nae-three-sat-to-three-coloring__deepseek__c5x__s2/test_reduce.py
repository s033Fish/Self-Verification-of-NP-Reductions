"""Test the correctness of the NAE-3-SAT to 3-Coloring reduction.

The script implements brute‑force solvers for both problems based on the
definitions in ``problems.py`` and then checks that for a collection of
random small instances the answer on the original instance matches the answer
on the reduced graph.

If all tests pass the script prints a JSON object suitable for the required
``verdict.json`` file.
"""

from __future__ import annotations

import json
import random
import sys
from typing import List, Tuple

import itertools
import problems
import reduce


def nae3sat_bruteforce(instance: dict) -> bool:
    """Return True iff the NAE‑3‑SAT instance is satisfiable.

    The instance format is ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``
    where each literal is a signed integer.  We try every assignment of
    ``True``/``False`` to the variables ``1..m``.
    """
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            vals = []
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                vals.append(val if lit > 0 else (not val))
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False


def three_coloring_bruteforce(instance: dict) -> bool:
    """Return True iff the graph is 3‑colorable.

    Implements a simple back‑tracking search; this is much faster than trying
    all 3^n colourings for the graphs produced by the reduction.
    """
    n: int = instance["n"]
    adj: List[set[int]] = [set() for _ in range(n)]
    for u, v in (tuple(e) for e in instance["edges"]):
        adj[u].add(v)
        adj[v].add(u)
    colors: List[int | None] = [None] * n

    def backtrack(v: int) -> bool:
        if v == n:
            return True
        for c in (0, 1, 2):
            if any(colors[nb] == c for nb in adj[v] if colors[nb] is not None):
                continue
            colors[v] = c
            if backtrack(v + 1):
                return True
            colors[v] = None
        return False

    return backtrack(0)


def generate_random_instances(num_trials: int, max_vars: int, max_clauses: int) -> List[dict]:
    """Generate a list of random NAE‑3‑SAT instances.

    Parameters bound the size of each instance. Random sampling keeps the test
    suite fast while still exercising many different shapes.
    """
    instances: List[dict] = []
    for _ in range(num_trials):
        m = random.randint(0, max_vars)
        clauses: List[List[int]] = []
        for _ in range(random.randint(0, max_clauses)):
            if m < 3:
                break
            vars_combo = random.sample(range(1, m + 1), 3)
            signs = [random.choice([1, -1]) for _ in range(3)]
            clause = [signs[i] * vars_combo[i] for i in range(3)]
            clauses.append(clause)
        instances.append({"num_vars": m, "clauses": clauses})
    return instances


def main() -> None:
    # Use a modest number of trials to keep runtime reasonable.
    test_instances = generate_random_instances(num_trials=50, max_vars=5, max_clauses=4)
    tests_run = 0
    tests_passed = 0
    all_ok = True
    for inst in test_instances:
        try:
            problems.SOURCE.validate(inst)
        except Exception:
            continue
        ans_src = nae3sat_bruteforce(inst)
        reduced = reduce.reduce(inst)
        try:
            problems.TARGET.validate(reduced)
        except Exception:
            print("Reduced instance invalid", file=sys.stderr)
            raise
        ans_tgt = three_coloring_bruteforce(reduced)
        tests_run += 1
        if ans_src == ans_tgt:
            tests_passed += 1
        else:
            all_ok = False
            print(json.dumps({"instance": inst, "reduced": reduced, "src": ans_src, "tgt": ans_tgt}, indent=2), file=sys.stderr)
    verdict = {"verified": all_ok, "tests_run": tests_run, "tests_passed": tests_passed}
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
