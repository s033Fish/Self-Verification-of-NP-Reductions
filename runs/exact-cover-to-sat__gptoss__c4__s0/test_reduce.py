import itertools
import random
import json
from problems import ExactCover, Sat
from reduce import reduce

def exact_cover_bruteforce(instance):
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    # Represent each set as a set of elements
    set_objs = [set(s) for s in sets]
    for mask in range(1 << n):
        chosen = []
        union = set()
        ok = True
        for i in range(n):
            if mask >> i & 1:
                s = set_objs[i]
                # check disjointness
                if union & s:
                    ok = False
                    break
                union |= s
                chosen.append(i)
        if not ok:
            continue
        if len(union) == u:
            return True
    # Edge case u=0 is always yes (choose no sets)
    return u == 0

def sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # empty clause makes unsat
    for clause in clauses:
        if len(clause) == 0:
            return False
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    # formula with no clauses is satisfiable
    return len(clauses) == 0


def random_exact_cover_instance(max_u=4, max_sets=5):
    u = random.randint(0, max_u)
    sets = []
    for _ in range(random.randint(0, max_sets)):
        # generate a random subset (may be empty)
        subset = [i for i in range(u) if random.choice([True, False])]
        sets.append(subset)
    return {"universe_size": u, "sets": sets}

def run_tests(num=200):
    passed = 0
    for _ in range(num):
        inst = random_exact_cover_instance()
        ExactCover.validate(inst)
        ans1 = exact_cover_bruteforce(inst)
        red = reduce(inst)
        Sat.validate(red)
        ans2 = sat_bruteforce(red)
        if ans1 == ans2:
            passed += 1
        else:
            print("Mismatch!", json.dumps(inst), json.dumps(red), ans1, ans2)
            break
    return passed, num

if __name__ == "__main__":
    passed, total = run_tests(500)
    print(f"{passed}/{total} tests passed")
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
