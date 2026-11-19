import random
import itertools
import json
import sys
import problems
from reduce import reduce

def solve_3sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            vals = [(assign[abs(l)-1] if l > 0 else not assign[abs(l)-1]) for l in clause]
            if not any(vals):
                ok = False
                break
        if ok:
            return True
    return False

def solve_naesat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            vals = [(assign[abs(l)-1] if l > 0 else not assign[abs(l)-1]) for l in clause]
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False

def random_instance(num_vars, num_clauses):
    clauses = []
    vars_range = list(range(1, num_vars + 1))
    for _ in range(num_clauses):
        vars_selected = random.sample(vars_range, 3)
        clause = []
        for v in vars_selected:
            sign = random.choice([1, -1])
            clause.append(sign * v)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}

random.seed(0)
passed = 0
failed = 0
failed_cases = []
for m in range(0, 5):
    for num_clauses in range(0, 5):
        for _ in range(30):
            if num_clauses > 0 and m < 3:
                continue  # invalid according to ThreeSat definition
            inst = random_instance(m, num_clauses)
            try:
                problems.ThreeSat.validate(inst)
            except Exception:
                continue
            reduced = reduce(inst)
            problems.NaeThreeSat.validate(reduced)
            ans1 = solve_3sat(inst)
            ans2 = solve_naesat(reduced)
            if ans1 == ans2:
                passed += 1
            else:
                failed += 1
                failed_cases.append({"inst": inst, "reduced": reduced, "ans1": ans1, "ans2": ans2})
verdict = {
    "verified": failed == 0,
    "tests_run": passed + failed,
    "tests_passed": passed,
}
print(json.dumps(verdict, indent=2))
if failed:
    print("Failed cases (first few):", file=sys.stderr)
    for c in failed_cases[:5]:
        print(c, file=sys.stderr)
    sys.exit(1)
