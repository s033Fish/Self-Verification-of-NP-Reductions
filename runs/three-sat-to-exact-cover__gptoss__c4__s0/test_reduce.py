import itertools
import json
import random
from problems import ThreeSat, ExactCover
from reduce import reduce

def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
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

def solve_exact_cover(instance):
    u = instance["universe_size"]
    sets = instance["sets"]
    n_sets = len(sets)
    # brute force over subsets (limit to small sizes)
    for r in range(n_sets + 1):
        for combo in itertools.combinations(range(n_sets), r):
            covered = [0] * u
            good = True
            for idx in combo:
                for e in sets[idx]:
                    if covered[e]:
                        good = False
                        break
                    covered[e] = 1
                if not good:
                    break
            if good and all(covered):
                return True
    return False

def random_three_sat(m, n_clauses):
    clauses = []
    for _ in range(n_clauses):
        # ensure we have at least 3 distinct variables
        vars = random.sample(range(1, m+1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

random.seed(0)

tests = 0
passed = 0
for m in range(0, 5):
    for n in range(0, 5):
        for _ in range(5):
            # skip impossible instances where m < 3 but n>0 (cannot form 3‑literal clauses)
            if m < 3 and n > 0:
                continue
            inst = random_three_sat(m, n)
            try:
                ThreeSat.validate(inst)
            except Exception:
                continue
            red = reduce(inst)
            ans1 = solve_three_sat(inst)
            ans2 = solve_exact_cover(red)
            tests += 1
            if ans1 == ans2:
                passed += 1
            else:
                print("Mismatch!", inst, ans1, ans2)
                raise SystemExit(1)
print(f"All {passed}/{tests} tests passed.")
verdict = {"verified": passed == tests, "tests_run": tests, "tests_passed": passed}
with open('verdict.json', 'w') as f:
    json.dump(verdict, f)
