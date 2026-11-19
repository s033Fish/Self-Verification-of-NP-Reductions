import itertools
import random
import sys
from problems import ThreeSat, NaeThreeSat
from reduce import reduce

def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        assign = [(bits >> i) & 1 == 1 for i in range(m)]  # variable i+1
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
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

def solve_nae_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        assign = [(bits >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in clauses:
            vals = []
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
                vals.append(val if lit > 0 else not val)
            # NAE condition: not all equal
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False

def random_three_sat_instance(m, num_clauses):
    """Generate a random 3‑SAT instance.
    For ``m < 3`` the definition of 3‑SAT requires that there be no clauses.
    """
    if m < 3:
        num_clauses = 0
    clauses = []
    vars = list(range(1, m + 1))
    for _ in range(num_clauses):
        chosen = random.sample(vars, 3)
        clause = []
        for v in chosen:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def main():
    random.seed(0)
    tests = 0
    passed = 0
    for m in range(0, 5):
        for _ in range(20):
            num_clauses = random.randint(0, 3)
            inst = random_three_sat_instance(m, num_clauses)
            ThreeSat.validate(inst)
            red = reduce(inst)
            NaeThreeSat.validate(red)
            ans_src = solve_three_sat(inst)
            ans_tgt = solve_nae_three_sat(red)
            tests += 1
            if ans_src == ans_tgt:
                passed += 1
            else:
                print("Mismatch!", inst, red, ans_src, ans_tgt)
                sys.exit(1)
    print(f"All {tests} tests passed: {passed} == {tests}")
    import json
    with open('verdict.json', 'w') as f:
        json.dump({"verified": True, "tests_run": tests, "tests_passed": passed}, f)

if __name__ == '__main__':
    main()
