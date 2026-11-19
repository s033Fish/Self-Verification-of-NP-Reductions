import random
import itertools
import json
from problems import ExactCover, Sat
from reduce import reduce


def exact_cover_bruteforce(instance):
    u = instance['universe_size']
    sets = instance['sets']
    n = len(sets)
    universe = set(range(u))
    for mask in range(1 << n):
        chosen = []
        covered = set()
        ok = True
        for i in range(n):
            if mask >> i & 1:
                s = sets[i]
                # check disjointness
                if any(x in covered for x in s):
                    ok = False
                    break
                covered.update(s)
                chosen.append(i)
        if not ok:
            continue
        if covered == universe:
            return True
    # also handle u==0 (empty universe) -> yes
    if u == 0:
        return True
    return False


def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # empty clause list -> satisfiable
    if not clauses:
        return True
    for assign in range(1 << m):
        # assign bit i => variable i+1 is True if bit set
        satisfied = True
        for clause in clauses:
            # empty clause -> unsatisfiable
            if not clause:
                satisfied = False
                break
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = bool(assign >> var & 1)
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def random_exact_cover_instance(max_u=4, max_sets=5):
    u = random.randint(0, max_u)
    sets = []
    for _ in range(random.randint(0, max_sets)):
        # generate a random subset (may be empty)
        subset = [i for i in range(u) if random.choice([True, False])]
        # random order
        random.shuffle(subset)
        sets.append(subset)
    # possibly duplicate a set
    if sets and random.random() < 0.3:
        sets.append(random.choice(sets).copy())
    return {"universe_size": u, "sets": sets}


def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        inst = random_exact_cover_instance()
        # validate source
        ExactCover.validate(inst)
        # reduce
        sat_inst = reduce(inst)
        Sat.validate(sat_inst)
        # compute answers
        ans_ec = exact_cover_bruteforce(inst)
        ans_sat = sat_bruteforce(sat_inst)
        if ans_ec == ans_sat:
            passed += 1
        else:
            print('Mismatch!')
            print('ExactCover instance:', json.dumps(inst, indent=2))
            print('SAT instance:', json.dumps(sat_inst, indent=2))
            print('ExactCover answer', ans_ec, 'SAT answer', ans_sat)
            break
    return passed, num_trials

if __name__ == '__main__':
    passed, total = run_tests()
    print(f"Passed {passed}/{total} tests")
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('Verdict written to verdict.json')
