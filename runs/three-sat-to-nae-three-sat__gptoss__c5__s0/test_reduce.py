"""Test suite for the reduction from ThreeSat to NaeThreeSat.

Implements brute‑force solvers for both problems and checks that the reduction
preserves the answer on many small instances.
"""

from __future__ import annotations

import itertools
import json
from typing import List, Dict

from problems import ThreeSat, NaeThreeSat
from reduce import reduce as reduction


def three_sat_bruteforce(instance: Dict) -> bool:
    """Return True iff the ThreeSat instance is satisfiable."""
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            satisfied = False
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1
                if (lit > 0 and val == 1) or (lit < 0 and val == 0):
                    satisfied = True
                    break
            if not satisfied:
                ok = False
                break
        if ok:
            return True
    return False


def nae_three_sat_bruteforce(instance: Dict) -> bool:
    """Return True iff the NAE‑3‑SAT instance is satisfiable."""
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            values = []
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1
                # literal evaluates to True if its sign matches the assignment
                values.append((lit > 0 and val == 1) or (lit < 0 and val == 0))
            # NAE satisfied when not all equal (i.e., not all True and not all False)
            if all(values) or not any(values):
                ok = False
                break
        if ok:
            return True
    return False


def generate_all_three_sat_instances(max_vars: int = 3, max_clauses: int = 3) -> List[Dict]:
    """Generate every valid ThreeSat instance with up to ``max_vars`` variables.
    For ``m < 3`` only the empty formula is valid. For ``m >= 3`` generate all
    possible clauses (three distinct variables with any sign) and all multisets
    of length up to ``max_clauses`` (allow repetitions).
    """
    instances: List[Dict] = []
    for m in range(max_vars + 1):
        if m < 3:
            instances.append({"num_vars": m, "clauses": []})
            continue
        clause_set: List[List[int]] = []
        for vars_tuple in itertools.combinations(range(1, m + 1), 3):
            for signs in itertools.product([1, -1], repeat=3):
                clause = [signs[i] * vars_tuple[i] for i in range(3)]
                clause_set.append(clause)
        for length in range(max_clauses + 1):
            for mult in itertools.product(clause_set, repeat=length):
                instances.append({"num_vars": m, "clauses": [list(c) for c in mult]})
    return instances


def main() -> None:
    instances = generate_all_three_sat_instances()
    total = len(instances)
    passed = 0
    for inst in instances:
        ThreeSat.validate(inst)
        reduced = reduction(inst)
        NaeThreeSat.validate(reduced)
        src_ans = three_sat_bruteforce(inst)
        tgt_ans = nae_three_sat_bruteforce(reduced)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Counter‑example found:")
            print(json.dumps({"instance": inst, "reduced": reduced, "src": src_ans, "tgt": tgt_ans}, indent=2))
            break
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
