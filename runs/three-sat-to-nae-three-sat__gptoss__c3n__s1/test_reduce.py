import random
import itertools
from problems import ThreeSat, NaeThreeSat
from reduce import reduce

def solve_three_sat(instance):
    m = instance["num_vars"]
    for bits in range(1 << m):
        assign = [(bits >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in instance["clauses"]:
            sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
                if lit > 0 and val:
                    sat = True
                if lit < 0 and not val:
                    sat = True
                if sat:
                    break
            if not sat:
                ok = False
                break
        if ok:
            return True
    return False

def solve_nae_three_sat(instance):
    m = instance["num_vars"]
    for bits in range(1 << m):
        assign = [(bits >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in instance["clauses"]:
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

def random_instance(m, clause_count):
    # generate random clauses respecting 3 distinct vars
    clauses = []
    for _ in range(clause_count):
        vars = random.sample(range(1, m+1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def test_random():
    random.seed(0)
    total = 0
    passed = 0
    for m in range(0, 5):
        max_clauses = 5
        for clause_cnt in range(0, max_clauses+1):
            for _ in range(200):
                inst = random_instance(m if m>=3 else 3, clause_cnt)  # ensure >=3 vars for clauses
                # adjust num_vars to m (allow unused vars)
                inst["num_vars"] = m
                # validate
                try:
                    ThreeSat.validate(inst)
                except Exception:
                    continue
                red = reduce(inst)
                ThreeSat.validate(inst)
                NaeThreeSat.validate(red)
                ans_src = solve_three_sat(inst)
                ans_tgt = solve_nae_three_sat(red)
                total += 1
                if ans_src == ans_tgt:
                    passed += 1
                else:
                    print("Mismatch!", inst, red, ans_src, ans_tgt)
                    return False
    print(f"All {passed}/{total} random tests passed")
    return True

if __name__ == "__main__":
    ok = test_random()
    # write verdict
    import json
    verdict = {"verified": ok, "tests_run": 1, "tests_passed": 1 if ok else 0}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
