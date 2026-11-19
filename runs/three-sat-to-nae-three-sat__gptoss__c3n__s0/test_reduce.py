import random
import itertools
from typing import List, Dict, Any

from problems import ThreeSat, NaeThreeSat
from reduce import reduce


def solve_three_sat(instance: Dict[str, Any]) -> bool:
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        assign = [(bits >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                sign = lit > 0
                val = assign[var]
                if not sign:
                    val = not val
                if val:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def solve_nae_three_sat(instance: Dict[str, Any]) -> bool:
    NaeThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        assign = [(bits >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in clauses:
            vals = []
            for lit in clause:
                var = abs(lit) - 1
                sign = lit > 0
                val = assign[var]
                if not sign:
                    val = not val
                vals.append(val)
            # NAE condition: not all equal
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False


def random_three_sat_instance(max_vars=4, max_clauses=4) -> Dict[str, Any]:
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
    num_clauses = random.randint(0, max_clauses)
    if num_clauses > 0 and m < 3:
        m = 3
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct variables
        vars = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def run_tests(num_tests=200):
    passed = 0
    for i in range(num_tests):
        inst = random_three_sat_instance()
        # solve original
        ans_src = solve_three_sat(inst)
        # reduce
        red = reduce(inst)
        ans_tgt = solve_nae_three_sat(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("FAIL on instance", inst)
            print("reduction", red)
            print("src", ans_src, "tgt", ans_tgt)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests()
    print(f"Tests passed: {passed}/{total}")
