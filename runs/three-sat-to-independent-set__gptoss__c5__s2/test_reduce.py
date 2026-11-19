"""Tests for the reduction from ThreeSat to IndependentSet.

The test suite implements brute‑force solvers for both problems based on the
formal definitions in ``problems.py``.  For a collection of small random
instances it checks that the answer to the source instance matches the answer
to the reduced target instance produced by ``reduce.py``.

If all checks pass the reduction is considered verified.
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

# Ensure the repository root is on the PYTHONPATH.
sys.path.append(str(Path(__file__).parent))

from problems import ThreeSat, IndependentSet
from reduce import reduce as reduce_instance


def three_sat_bruteforce(instance: dict) -> bool:
    """Return True iff the 3‑SAT instance is satisfiable.

    The instance follows the format defined by :class:`ThreeSat`.
    """
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Enumerate all possible assignments of m boolean variables.
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0 and val:
                    clause_ok = True
                    break
                if lit < 0 and not val:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def independent_set_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has an independent set of size at least k.
    """
    IndependentSet.validate(instance)
    n = instance["n"]
    edges = {(u, v) for u, v in (tuple(e) for e in instance["edges"]) }
    edges |= {(v, u) for u, v in edges}
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    for r in range(k, n + 1):
        for subset in itertools.combinations(range(n), r):
            good = True
            for i in range(len(subset)):
                for j in range(i + 1, len(subset)):
                    if (subset[i], subset[j]) in edges:
                        good = False
                        break
                if not good:
                    break
            if good:
                return True
    return False


def random_three_sat_instance(max_vars: int = 5, max_clauses: int = 5) -> dict:
    """Generate a random well‑formed 3‑SAT instance.

    Variables are numbered 1..m.  Each clause contains three distinct literals
    on distinct variables, and no clause contains both a variable and its
    negation.
    """
    m = random.randint(0, max_vars)
    if m < 3:
        return {"num_vars": m, "clauses": []}
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        vars_ = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, -2, 3], [-1, 2, -3]]},
    ]
    for inst in edge_cases:
        total += 1
        sat = three_sat_bruteforce(inst)
        red = reduce_instance(inst)
        indep = independent_set_bruteforce(red)
        if sat == indep:
            passed += 1
        else:
            print("FAIL edge case", inst, sat, indep, file=sys.stderr)
    for _ in range(200):
        inst = random_three_sat_instance()
        total += 1
        sat = three_sat_bruteforce(inst)
        red = reduce_instance(inst)
        indep = independent_set_bruteforce(red)
        if sat == indep:
            passed += 1
        else:
            print("FAIL random", json.dumps(inst), sat, indep, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()

