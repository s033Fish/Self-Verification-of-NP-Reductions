import random
import itertools
import json
import sys
from problems import ThreeSat, OneInThreeSat
from reduce import reduce

def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assign in itertools.product([0, 1], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
                if lit > 0 and val == 1:
                    clause_ok = True
                if lit < 0 and val == 0:
                    clause_ok = True
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

def solve_one_in_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assign in itertools.product([0, 1], repeat=m):
        ok = True
        for clause in clauses:
            cnt = sum(assign[v-1] for v in clause)
            if cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False

def random_three_sat(m, max_clauses=5):
    """Generate a random 3‑SAT instance respecting the problem constraints.
    For ``m < 3`` the definition of 3‑SAT requires that no clause can be
    formed, so we simply return an instance with an empty clause list.
    """
    if m < 3:
        return {"num_vars": m, "clauses": []}
    clauses = []
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        vars = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def main():
    random.seed(0)
    tests = 0
    passed = 0
    # systematic small tests
    for m in range(0, 5):
        for _ in range(100):
            inst = random_three_sat(m, max_clauses=4)
            ThreeSat.validate(inst)
            ans_src = solve_three_sat(inst)
            red = reduce(inst)
            OneInThreeSat.validate(red)
            ans_tgt = solve_one_in_three_sat(red)
            tests += 1
            if ans_src == ans_tgt:
                passed += 1
            else:
                print("Mismatch!", inst, ans_src, ans_tgt)
                sys.exit(1)
    # edge case: no clauses with various m
    for m in range(0, 6):
        inst = {"num_vars": m, "clauses": []}
        ans_src = solve_three_sat(inst)
        red = reduce(inst)
        ans_tgt = solve_one_in_three_sat(red)
        tests += 1
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Edge mismatch", inst)
            sys.exit(1)
    verdict = {"verified": passed == tests, "tests_run": tests, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == '__main__':
    main()
