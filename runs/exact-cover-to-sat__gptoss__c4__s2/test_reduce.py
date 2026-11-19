import itertools
import random
import json
from problems import ExactCover, Sat
from reduce import reduce

def exact_cover_bruteforce(instance):
    u = instance['universe_size']
    sets = instance['sets']
    n = len(sets)
    universe = set(range(u))
    # iterate over all subsets of sets (represented by bitmask)
    for bits in range(1 << n):
        chosen = []
        covered = set()
        ok = True
        for i in range(n):
            if bits >> i & 1:
                s = set(sets[i])
                # check disjointness
                if covered & s:
                    ok = False
                    break
                covered |= s
                chosen.append(i)
        if not ok:
            continue
        if covered == universe:
            return True
    # also handle u==0 (empty universe) which is trivially yes
    if u == 0:
        return True
    return False

def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # generate all assignments as tuple of booleans length m (index 0 -> var1)
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]
        satisfied = True
        for clause in clauses:
            # empty clause -> unsatisfied
            if len(clause) == 0:
                satisfied = False
                break
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    # formula with no clauses is satisfiable
    if len(clauses) == 0:
        return True
    return False

def random_exact_cover(max_u=4, max_sets=5):
    u = random.randint(0, max_u)
    n = random.randint(0, max_sets)
    sets = []
    for _ in range(n):
        # each set random subset of universe
        subset = [i for i in range(u) if random.random() < 0.5]
        sets.append(subset)
    return {"universe_size": u, "sets": sets}

def run_tests(num=200):
    passed = 0
    for _ in range(num):
        inst = random_exact_cover()
        ExactCover.validate(inst)
        sat_inst = reduce(inst)
        Sat.validate(sat_inst)
        ec_res = exact_cover_bruteforce(inst)
        sat_res = sat_bruteforce(sat_inst)
        if ec_res == sat_res:
            passed += 1
        else:
            print('Mismatch!')
            print('ExactCover instance:', json.dumps(inst))
            print('Reduced SAT instance:', json.dumps(sat_inst))
            print('ExactCover result', ec_res, 'SAT result', sat_res)
            break
    return passed, num

if __name__ == '__main__':
    passed, total = run_tests(500)
    print(f'Passed {passed}/{total} tests')
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('Verdict written to verdict.json')
