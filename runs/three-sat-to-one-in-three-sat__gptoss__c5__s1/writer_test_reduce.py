import itertools
import random
import json
from problems import ThreeSat, OneInThreeSat
from reduce import reduce


def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            # clause list of literals
            satisfied = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0 and val:
                    satisfied = True
                if lit < 0 and not val:
                    satisfied = True
                if satisfied:
                    break
            if not satisfied:
                ok = False
                break
        if ok:
            return True
    return False


def solve_one_in_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            true_count = sum(bits[var-1] for var in clause)
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def random_three_sat_instance(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
    if m < 3:
        m = 3 if random.random() < 0.5 else m
    clauses = []
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        # pick 3 distinct vars
        vars_ = random.sample(range(1, m+1), 3)
        clause = []
        for v in vars_:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        inst = random_three_sat_instance()
        # validate
        ThreeSat.validate(inst)
        reduced = reduce(inst)
        OneInThreeSat.validate(reduced)
        ans_src = solve_three_sat(inst)
        ans_tgt = solve_one_in_three_sat(reduced)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("FAIL", inst, reduced, ans_src, ans_tgt)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests(500)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
