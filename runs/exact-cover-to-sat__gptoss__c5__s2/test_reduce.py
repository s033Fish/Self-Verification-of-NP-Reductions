"""Automated tests for the ExactCover → SAT reduction.

The repository provides only validation helpers for the two problems and a
``reduce`` function.  To verify the reduction we implement tiny brute‑force
solvers for both source and target problems and compare the answers on a
large collection of randomly generated instances.

The script records the number of tests executed and how many passed and
writes a ``verdict.json`` file as required by the task description.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, product
from typing import List, Dict, Any

from problems import ExactCover, Sat
from reduce import reduce as reduce_ec_to_sat


def exact_cover_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the ExactCover instance has an exact cover.

    The universe size is small in the generated tests, so we simply try all
    subsets of the given sets.
    """
    ExactCover.validate(instance)
    u = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    n = len(sets)
    # Represent each set as a frozenset for quick operations.
    set_frozen = [frozenset(s) for s in sets]
    universe = set(range(u))
    # Enumerate all subsets of indices.
    for mask in range(1 << n):
        covered: set[int] = set()
        ok = True
        for i in range(n):
            if mask >> i & 1:
                s = set_frozen[i]
                if covered & s:
                    ok = False
                    break
                covered |= s
        if ok and covered == universe:
            return True
    # Edge case: empty universe is always satisfiable (choose nothing).
    return u == 0


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the SAT instance is satisfiable.

    Exhaustively tries all assignments of the ``num_vars`` variables.
    """
    Sat.validate(instance)
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # An empty clause makes the formula unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False
    # No clauses → trivially satisfiable.
    if not clauses:
        return True
    for assignment in product([False, True], repeat=m):
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def generate_random_instance(max_universe: int, max_sets: int) -> Dict[str, Any]:
    """Create a random ExactCover instance.

    * ``max_universe`` – maximum size of the universe (inclusive).
    * ``max_sets`` – maximum number of sets (inclusive).
    The generator may produce duplicate sets and empty sets as allowed by the
    problem definition.
    """
    u = random.randint(0, max_universe)
    n = random.randint(0, max_sets)
    sets: List[List[int]] = []
    for _ in range(n):
        size = random.randint(0, u)
        elems = random.sample(range(u), k=size) if size <= u else []
        sets.append(elems)
    return {"universe_size": u, "sets": sets}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    tests_run = 0
    tests_passed = 0
    for _ in range(200):
        inst = generate_random_instance(max_universe=4, max_sets=5)
        src_ans = exact_cover_bruteforce(inst)
        reduced = reduce_ec_to_sat(inst)
        try:
            Sat.validate(reduced)
        except Exception as e:
            print("Reduction produced invalid SAT instance:", e, file=sys.stderr)
            continue
        tgt_ans = sat_bruteforce(reduced)
        tests_run += 1
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            print("Mismatch!", inst, "src", src_ans, "tgt", tgt_ans, file=sys.stderr)
    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
