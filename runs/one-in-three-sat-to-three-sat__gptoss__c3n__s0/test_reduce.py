import random
import itertools
import json
from problems import OneInThreeSat, ThreeSat, InvalidInstance
from reduce import reduce


def is_sat_one_in_three(instance):
    OneInThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # iterate over all assignments of m variables (True/False)
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for a, b, c in clauses:
            cnt = bits[a-1] + bits[b-1] + bits[c-1]
            if cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def is_sat_three_sat(instance):
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for lit1, lit2, lit3 in clauses:
            def lit_val(lit):
                var = abs(lit) - 1
                val = bits[var]
                return val if lit > 0 else (not val)
            if not (lit_val(lit1) or lit_val(lit2) or lit_val(lit3)):
                ok = False
                break
        if ok:
            return True
    return False


def random_one_in_three_instance(max_vars=4, max_clauses=5):
    # choose number of vars m (could be 0)
    m = random.randint(0, max_vars)
    # generate random number of clauses (could be 0)
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        # need at least 3 vars if clauses exist, ensure m>=3 else generate empty list
        if m < 3:
            # cannot have clause, break
            break
        # pick 3 distinct vars from 1..m
        clause = random.sample(range(1, m+1), 3)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for i in range(num_tests):
        src = random_one_in_three_instance()
        # ensure validation passes (may raise if m<3 and clauses nonempty)
        try:
            OneInThreeSat.validate(src)
        except InvalidInstance:
            continue  # skip malformed generated instance
        tgt = reduce(src)
        src_sat = is_sat_one_in_three(src)
        tgt_sat = is_sat_three_sat(tgt)
        if src_sat == tgt_sat:
            passed += 1
        else:
            print("Mismatch on test", i)
            print("src", src)
            print("tgt", tgt)
            print(src_sat, tgt_sat)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests()
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result, indent=2))
    # write verdict.json
    with open("verdict.json", "w") as f:
        json.dump(result, f)
