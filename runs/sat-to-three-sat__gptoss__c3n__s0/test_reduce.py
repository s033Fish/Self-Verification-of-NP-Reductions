import itertools
import random
import sys
from typing import List, Dict, Any

from problems import Sat, ThreeSat
from reduce import reduce


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    Sat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge: no clauses -> sat
    if not clauses:
        return True
    for assignment in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            # empty clause is unsat
            if len(clause) == 0:
                ok = False
                break
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0 and val:
                    clause_ok = True
                if lit < 0 and not val:
                    clause_ok = True
                if clause_ok:
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def three_sat_bruteforce(instance: Dict[str, Any]) -> bool:
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    if not clauses:
        return True
    for assignment in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            # clause length is guaranteed 3
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0 and val:
                    clause_ok = True
                if lit < 0 and not val:
                    clause_ok = True
                if clause_ok:
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def random_sat_instance(max_vars=4, max_clauses=5, max_lits=5) -> Dict[str, Any]:
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        k = random.randint(0, max_lits)
        clause = []
        for __ in range(k):
            if m == 0:
                # no variables, but literals must be within range -> skip
                continue
            var = random.randint(1, m)
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for i in range(num_tests):
        src = random_sat_instance()
        try:
            tgt = reduce(src)
        except Exception as e:
            print(f"Reduction raised on test {i}: {e}")
            sys.exit(1)
        src_ans = sat_bruteforce(src)
        tgt_ans = three_sat_bruteforce(tgt)
        if src_ans != tgt_ans:
            print("Mismatch on test", i)
            print("source", src)
            print("target", tgt)
            print("src_ans", src_ans, "tgt_ans", tgt_ans)
            sys.exit(1)
        passed += 1
    print(f"All {passed} tests passed.")
    # write verdict.json
    import json
    verdict = {"verified": True, "tests_run": passed, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    run_tests()
