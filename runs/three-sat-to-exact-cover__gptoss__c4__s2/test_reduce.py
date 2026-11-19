import itertools
import random
import sys
from problems import ThreeSat, ExactCover
from reduce import reduce


def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1
                if lit > 0 and val == 1:
                    clause_ok = True
                    break
                if lit < 0 and val == 0:
                    clause_ok = True
                    break
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
    for r in range(n + 1):
        for combo in itertools.combinations(range(n), r):
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


def random_three_sat(m, num_clauses):
    clauses = []
    vars_list = list(range(1, m + 1))
    for _ in range(num_clauses):
        # pick 3 distinct vars (if possible)
        v = random.sample(vars_list, 3)
        clause = []
        for var in v:
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    random.seed(0)
    tests = 0
    passed = 0
    for m in range(0, 5):
        max_clauses = 5
        for num_clauses in range(0, max_clauses + 1):
            if num_clauses > 0 and m < 3:
                continue
            for _ in range(20):
                inst = random_three_sat(m, num_clauses)
                ThreeSat.validate(inst)
                red = reduce(inst)
                ExactCover.validate(red)
                ans_src = solve_three_sat(inst)
                ans_tgt = solve_exact_cover(red)
                tests += 1
                if ans_src == ans_tgt:
                    passed += 1
                else:
                    print("Mismatch!", inst, red, ans_src, ans_tgt)
                    sys.exit(1)
    print(f"All {tests} tests passed: {passed} succeeded")
    with open('verdict.json', 'w') as f:
        f.write('{"verified": true, "tests_run": %d, "tests_passed": %d}' % (tests, passed))

if __name__ == '__main__':
    main()
