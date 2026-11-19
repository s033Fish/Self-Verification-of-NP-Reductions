"""Test the reduction from 3‑SAT to Independent Set.

The repository provides only validation helpers for the two problems and a
reduction implementation.  To verify the reduction we implement brute‑force
solvers for both source and target problems and then generate a large number
of small random instances.  For each instance we:

1. Validate the instance using the problem classes (to ensure we only test
   well‑formed inputs).
2. Compute the answer for the 3‑SAT instance with a naïve exhaustive search.
3. Apply ``reduce`` to obtain an Independent‑Set instance.
4. Compute the answer for the Independent‑Set instance with another exhaustive
   search.
5. Check that the two answers agree.

If every generated instance passes the check we consider the reduction to be
correct for the tested domain and set ``verified`` to ``true`` in the final
``verdict.json`` file.

The test is deliberately limited to small instances (up to 4 variables and up
to 4 clauses) because the exhaustive search is exponential.  This still gives
reasonable confidence because the reduction is combinatorial and works for
any size; failures would appear on tiny instances as well.
"""

from __future__ import annotations

import json
import random
import itertools
from pathlib import Path

from problems import ThreeSat, IndependentSet
from reduce import reduce as reduce_instance


def three_sat_bruteforce(instance: dict) -> bool:
    """Return True iff the 3‑SAT instance is satisfiable.

    The instance is assumed to be validated and to contain ``num_vars`` and
    ``clauses`` as described in the problem definition.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            satisfied = False
            for lit in clause:
                var = abs(lit) - 1
                val = (mask >> var) & 1
                if (lit > 0 and val) or (lit < 0 and not val):
                    satisfied = True
                    break
            if not satisfied:
                ok = False
                break
        if ok:
            return True
    return False


def independent_set_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has an independent set of size at least k.
    """
    n = instance["n"]
    edges = {(u, v) for u, v in (tuple(e) for e in instance["edges"])}
    edges |= {(v, u) for u, v in edges}
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            good = True
            for u, v in itertools.combinations(subset, 2):
                if (u, v) in edges:
                    good = False
                    break
            if good:
                return True
    return False


def random_three_sat_instance(max_vars: int = 4, max_clauses: int = 4) -> dict:
    """Generate a random well‑formed 3‑SAT instance.

    The generation respects the constraints: each clause has three distinct
    variables and does not contain both a variable and its negation.
    """
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    if num_clauses > 0 and m < 3:
        m = 3
    clauses = []
    for _ in range(num_clauses):
        vars_ = random.sample(range(1, m + 1), 3)
        lits = []
        for v in vars_:
            lits.append(random.choice([1, -1]) * v)
        clauses.append(lits)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        instance = random_three_sat_instance()
        ThreeSat.validate(instance)
        sat = three_sat_bruteforce(instance)
        reduced = reduce_instance(instance)
        IndependentSet.validate(reduced)
        indep = independent_set_bruteforce(reduced)
        total += 1
        if sat == indep:
            passed += 1
        else:
            print("Mismatch!", json.dumps({"src": instance, "red": reduced, "sat": sat, "indep": indep}, indent=2))
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
