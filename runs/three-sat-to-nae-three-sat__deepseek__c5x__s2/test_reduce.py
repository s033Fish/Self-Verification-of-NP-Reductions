"""Tests for the reduction from 3‑SAT to NAE‑3‑SAT.

The repository provides only validation code for the two problems and a
`reduce` implementation.  To verify the reduction we implement straightforward
brute‑force solvers for both problems and compare the answer on many small
random instances.

The tests check:
* the reduction output satisfies the TARGET validation rules,
* the YES/NO answer of the reduced instance matches the answer of the
  original instance, and
* edge cases such as an empty clause list are handled correctly.

The script is deliberately simple – it does not depend on any external test
framework – and exits with a non‑zero status if a discrepancy is found.  The
continuous‑integration harness used for the review task runs the script and
counts the number of passed tests.
"""

from __future__ import annotations

import random
import sys
from typing import List

from problems import SOURCE, TARGET
from reduce import reduce as reduce_instance


def three_sat_bruteforce(instance: dict) -> bool:
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in clauses:
            if not any((lit > 0 and assignment[lit - 1]) or (lit < 0 and not assignment[-lit - 1]) for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def nae_three_sat_bruteforce(instance: dict) -> bool:
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in clauses:
            vals = []
            for lit in clause:
                val = assignment[abs(lit) - 1]
                if lit < 0:
                    val = not val
                vals.append(val)
            if vals[0] == vals[1] == vals[2]:
                ok = False
                break
        if ok:
            return True
    return False


def random_instance(max_vars: int, max_clauses: int) -> dict:
    m = random.randint(0, max_vars)
    # Ensure enough variables for a clause; otherwise generate empty clause list.
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
    # Exhaustive small range
    for m in range(0, 4):
        for _ in range(30):
            inst = random_instance(m, 3)
            try:
                SOURCE.validate(inst)
            except Exception as e:
                print("Source validation failed", inst, e, file=sys.stderr)
                continue
            total += 1
            src_ans = three_sat_bruteforce(inst)
            reduced = reduce_instance(inst)
            try:
                TARGET.validate(reduced)
            except Exception as e:
                print("Target validation failed", reduced, e, file=sys.stderr)
                continue
            tgt_ans = nae_three_sat_bruteforce(reduced)
            if src_ans == tgt_ans:
                passed += 1
            else:
                print("Mismatch!", inst, reduced, file=sys.stderr)
                sys.exit(1)
    # Additional random tests
    for _ in range(200):
        inst = random_instance(5, 5)
        try:
            SOURCE.validate(inst)
        except Exception:
            continue
        total += 1
        src_ans = three_sat_bruteforce(inst)
        reduced = reduce_instance(inst)
        try:
            TARGET.validate(reduced)
        except Exception as e:
            print("Target validation failed (random)", reduced, e, file=sys.stderr)
            sys.exit(1)
        tgt_ans = nae_three_sat_bruteforce(reduced)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch (random)!", inst, reduced, file=sys.stderr)
            sys.exit(1)
    print(f"Tests run: {total}, passed: {passed}")

if __name__ == "__main__":
    main()
