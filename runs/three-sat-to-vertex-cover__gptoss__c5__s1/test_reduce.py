"""Automated tests for the reduction from 3‑SAT to Vertex Cover.

The repository provides only validation functions for the two problems
and a reduction implementation.  To verify the reduction we implement
brute‑force solvers for both source and target problems and compare the
answers on a large collection of small random instances as well as a few
hand‑crafted edge cases.

The script records how many tests were executed and how many passed and
writes a ``verdict.json`` file in the repository root.  The format of the
verdict matches the specification of the task:

```
{"verified": <bool>, "tests_run": <int>, "tests_passed": <int>}
```

If any test fails, ``verified`` is ``false``.
"""

from __future__ import annotations

import json
import random
import itertools
from pathlib import Path
from typing import List, Dict

from problems import ThreeSat, VertexCover
from reduce import reduce as reduce_instance


def solve_three_sat(instance: Dict) -> bool:
    """Brute‑force SAT solver for the 3‑SAT instance.

    Returns ``True`` iff there exists an assignment satisfying all clauses.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1
                if lit > 0 and val == 1:
                    clause_ok = True
                    break
                if lit < 0 and val == 0:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def solve_vertex_cover(instance: Dict) -> bool:
    """Brute‑force solver for Vertex Cover.

    Returns ``True`` iff there exists a vertex cover of size at most ``k``.
    """
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    if not edges:
        return True
    if k >= n:
        return True
    vertices = list(range(n))
    for size in range(k + 1):
        for subset in itertools.combinations(vertices, size):
            covered = 0
            for u, v in edges:
                if u in subset or v in subset:
                    covered += 1
            if covered == len(edges):
                return True
    return False


def generate_random_three_sat(max_vars: int = 4, max_clauses: int = 4) -> Dict:
    """Create a random 3‑SAT instance respecting the format constraints.

    Variables are numbered from 1..m.  Each clause contains three distinct
    variables with random polarity.
    """
    m = random.randint(0, max_vars)
    if m < 3:
        return {"num_vars": m, "clauses": []}
    num_clauses = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        vars_selected = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_selected:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    total = 0
    passed = 0
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, -2, 3], [-1, 2, -3], [1, 2, -3]]},
    ]
    for instance in edge_cases:
        total += 1
        try:
            ThreeSat.validate(instance)
        except Exception as exc:
            print("Invalid edge case instance:", instance, exc)
            continue
        src_ans = solve_three_sat(instance)
        tgt = reduce_instance(instance)
        tgt_ans = solve_vertex_cover(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch on edge case", instance, src_ans, tgt_ans)
    for _ in range(200):
        instance = generate_random_three_sat()
        total += 1
        try:
            ThreeSat.validate(instance)
        except Exception:
            total -= 1
            continue
        src_ans = solve_three_sat(instance)
        tgt = reduce_instance(instance)
        tgt_ans = solve_vertex_cover(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Reduction failed for instance", instance)
            print("src", src_ans, "tgt", tgt_ans)
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
