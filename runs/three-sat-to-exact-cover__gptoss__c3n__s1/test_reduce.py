import itertools
import random
import json
import problems
from reduce import reduce

def solve_three_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
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
    u = instance['universe_size']
    sets = instance['sets']
    n = len(sets)
    universe = set(range(u))
    # try all subsets of sets (exponential, but small sizes only)
    for r in range(n+1):
        for combo in itertools.combinations(range(n), r):
            covered = set()
            disjoint = True
            for idx in combo:
                s = set(sets[idx])
                if covered & s:
                    disjoint = False
                    break
                covered |= s
            if disjoint and covered == universe:
                return True
    return False

def random_three_sat(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure if clauses >0 then m>=3 per spec, but we can still generate any
    # We'll generate clauses only if m>=1
    clauses = []
    if m == 0:
        return {'num_vars':0, 'clauses':[]}
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        # pick 3 distinct variables
        vars = random.sample(range(1, m+1), 3) if m>=3 else []
        if not vars:
            continue
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {'num_vars': m, 'clauses': clauses}

def main():
    random.seed(0)
    tests = 200
    passed = 0
    for i in range(tests):
        inst = random_three_sat()
        # validate source
        try:
            problems.ThreeSat.validate(inst)
        except Exception as e:
            print('Invalid source generated', inst, e)
            continue
        reduced = reduce(inst)
        # validate target
        problems.ExactCover.validate(reduced)
        ans_src = solve_three_sat(inst)
        ans_tgt = solve_exact_cover(reduced)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch on test', i)
            print('src', inst, ans_src)
            print('tgt', reduced, ans_tgt)
            break
    print('tests run', tests, 'passed', passed)
    # write verdict
    verdict = {
        "verified": passed == tests,
        "tests_run": tests,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
