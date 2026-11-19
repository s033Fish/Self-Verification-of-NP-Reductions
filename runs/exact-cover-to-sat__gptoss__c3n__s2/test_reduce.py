import random
import itertools
import json
from problems import ExactCover, Sat
from reduce import reduce


def exact_cover_bruteforce(instance):
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    # Edge case: empty universe is always yes
    if u == 0:
        return True
    # Preprocess sets as frozensets for efficiency
    set_frozens = [frozenset(s) for s in sets]
    for mask in range(1 << n):
        chosen = []
        union = set()
        ok = True
        for i in range(n):
            if mask >> i & 1:
                s = set_frozens[i]
                # if any element already covered, not disjoint
                if union & s:
                    ok = False
                    break
                union |= s
                chosen.append(s)
        if not ok:
            continue
        if len(union) == u and all(0 <= e < u for e in union):
            return True
    return False


def sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge case: empty clause list -> satisfiable
    if not clauses:
        return True
    for mask in range(1 << m):
        assignment = [(mask >> i) & 1 == 1 for i in range(m)]  # var i+1
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0 and val:
                    clause_ok = True
                    break
                if lit < 0 and not val:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def random_exact_cover_instance(max_u=4, max_n=5):
    u = random.randint(0, max_u)
    n = random.randint(0, max_n)
    sets = []
    for _ in range(n):
        # each set can be any subset of universe
        subset = [e for e in range(u) if random.choice([True, False])]
        sets.append(subset)
    return {"universe_size": u, "sets": sets}


def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        inst = random_exact_cover_instance()
        ExactCover.validate(inst)
        ec_ans = exact_cover_bruteforce(inst)
        sat_inst = reduce(inst)
        Sat.validate(sat_inst)
        sat_ans = sat_bruteforce(sat_inst)
        if ec_ans == sat_ans:
            passed += 1
        else:
            print("Mismatch!", inst, "=>", ec_ans, sat_ans)
            break
    return passed, num_trials

if __name__ == "__main__":
    passed, total = run_tests()
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
