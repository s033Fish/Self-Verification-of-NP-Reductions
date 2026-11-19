import random
import sys
import json

from problems import ExactCover, Sat
from reduce import reduce

def exact_cover_bruteforce(instance):
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    universe = set(range(u))
    for mask in range(1 << n):
        covered = set()
        ok = True
        for i in range(n):
            if mask & (1 << i):
                s = set(sets[i])
                if covered & s:
                    ok = False
                    break
                covered |= s
        if not ok:
            continue
        if covered == universe:
            return True
    return u == 0

def sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # empty clause -> unsat
    for clause in clauses:
        if len(clause) == 0:
            return False
    # no clauses -> sat
    if len(clauses) == 0:
        return True
    for assign in range(1 << m):
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = (assign >> var) & 1
                if lit > 0 and val == 1:
                    clause_sat = True
                    break
                if lit < 0 and val == 0:
                    clause_sat = True
                    break
            if not clause_sat:
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
        subset = [i for i in range(u) if random.choice([True, False])]
        sets.append(subset)
    return {"universe_size": u, "sets": sets}

def main():
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        inst = random_exact_cover_instance()
        ExactCover.validate(inst)
        src_ans = exact_cover_bruteforce(inst)
        sat_inst = reduce(inst)
        Sat.validate(sat_inst)
        tgt_ans = sat_bruteforce(sat_inst)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", inst, "->", sat_inst, src_ans, tgt_ans, file=sys.stderr)
        total += 1
    # edge cases
    edge_cases = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 1, "sets": [[]]},
        {"universe_size": 1, "sets": [[0], [0]]},
    ]
    for inst in edge_cases:
        ExactCover.validate(inst)
        src_ans = exact_cover_bruteforce(inst)
        sat_inst = reduce(inst)
        Sat.validate(sat_inst)
        tgt_ans = sat_bruteforce(sat_inst)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch edge!", inst, sat_inst, src_ans, tgt_ans, file=sys.stderr)
        total += 1
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == '__main__':
    main()
