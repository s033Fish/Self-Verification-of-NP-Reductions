import itertools
import random
import json
from problems import ThreeSat, ExactCover
from reduce import reduce

def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0 and val:
                    clause_ok = True
                if lit < 0 and not val:
                    clause_ok = True
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

def solve_exact_cover(instance):
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    # try all subsets of sets (up to 2^n, but n small in tests)
    for r in range(1 << n):
        chosen = []
        covered = [0] * u
        ok = True
        for i in range(n):
            if (r >> i) & 1:
                s = sets[i]
                # check overlap
                for e in s:
                    if covered[e]:
                        ok = False
                        break
                if not ok:
                    break
                for e in s:
                    covered[e] = 1
                chosen.append(s)
        if ok and all(covered_elem == 1 for covered_elem in covered):
            return True
    return False

def random_three_sat(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 0 clauses allowed
    c = random.randint(0, max_clauses)
    clauses = []
    for _ in range(c):
        # pick 3 distinct variables from 1..max(m,3) if m<3 still allowed? spec: if clauses exist need m>=3
        if m < 3:
            # ensure m >=3 when we have clauses
            m = 3
        vars = random.sample(range(1, m+1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        inst = random_three_sat()
        ThreeSat.validate(inst)
        reduced = reduce(inst)
        ExactCover.validate(reduced)
        ans1 = solve_three_sat(inst)
        ans2 = solve_exact_cover(reduced)
        if ans1 == ans2:
            passed += 1
        else:
            print("Mismatch!", json.dumps(inst), json.dumps(reduced), ans1, ans2)
            break
    return passed, num_trials

if __name__ == "__main__":
    passed, total = run_tests()
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
