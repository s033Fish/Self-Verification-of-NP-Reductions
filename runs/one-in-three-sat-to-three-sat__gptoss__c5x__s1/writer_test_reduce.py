import random
import itertools
import json
from problems import OneInThreeSat, ThreeSat
from reduce import reduce


def solve_one_in_three(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for a, b, c in clauses:
            # variables are 1-indexed
            vals = [bits[a-1], bits[b-1], bits[c-1]]
            if sum(vals) != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for l1, l2, l3 in clauses:
            def lit_val(l):
                v = abs(l) - 1
                val = bits[v]
                return val if l > 0 else not val
            if not (lit_val(l1) or lit_val(l2) or lit_val(l3)):
                ok = False
                break
        if ok:
            return True
    return False


def random_one_in_three_instance(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if we add clauses
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        if m < 3:
            # need at least 3 vars to make a clause, so break
            break
        vars = random.sample(range(1, m+1), 3)
        clauses.append(vars)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for i in range(num_tests):
        inst = random_one_in_three_instance()
        # validate source
        try:
            OneInThreeSat.validate(inst)
        except Exception as e:
            continue  # skip invalid generated (e.g., m<3 with clause)
        src_ans = solve_one_in_three(inst)
        red = reduce(inst)
        tgt_ans = solve_three_sat(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("FAIL on instance", inst)
            print("Reduced", red)
            print(src_ans, tgt_ans)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests(500)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
