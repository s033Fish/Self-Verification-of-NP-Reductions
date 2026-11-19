import itertools
import random
import json
from problems import ExactCover, Sat
from reduce import reduce


def exact_cover_bruteforce(instance):
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    # iterate over all subsets of sets
    for mask in range(1 << n):
        chosen = []
        for i in range(n):
            if mask & (1 << i):
                chosen.append(sets[i])
        # Check pairwise disjointness and covering
        covered = [0] * u
        ok = True
        for s in chosen:
            for e in s:
                if covered[e]:
                    ok = False
                    break
                covered[e] = 1
            if not ok:
                break
        if ok and all(covered):
            return True
    # Edge case u=0 always yes
    return u == 0


def sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # empty clause -> unsat
    for c in clauses:
        if len(c) == 0:
            return False
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
                if lit > 0 and val:
                    clause_ok = True
                    break
                if lit < 0 and not val:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    # No assignment works; edge case: no clauses -> yes
    return len(clauses) == 0


def random_exact_cover(u_max=4, set_count_max=5, trials=200):
    for _ in range(trials):
        u = random.randint(0, u_max)
        num_sets = random.randint(0, set_count_max)
        sets = []
        for _ in range(num_sets):
            # generate random subset
            subset = [i for i in range(u) if random.choice([True, False])]
            sets.append(subset)
        instance = {"universe_size": u, "sets": sets}
        # validate
        ExactCover.validate(instance)
        yield instance


def run_tests():
    total = 0
    passed = 0
    for instance in random_exact_cover():
        total += 1
        ec_ans = exact_cover_bruteforce(instance)
        sat_inst = reduce(instance)
        sat_ans = sat_bruteforce(sat_inst)
        if ec_ans == sat_ans:
            passed += 1
        else:
            print("Mismatch!", json.dumps(instance), "=>", ec_ans, sat_ans)
            print("SAT instance", json.dumps(sat_inst))
            break
    # also test some edge cases explicitly
    edge_cases = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[0]]},  # invalid set will be caught by validator
    ]
    for inst in edge_cases:
        try:
            ExactCover.validate(inst)
        except Exception:
            continue
        total += 1
        ec_ans = exact_cover_bruteforce(inst)
        sat_inst = reduce(inst)
        sat_ans = sat_bruteforce(sat_inst)
        if ec_ans == sat_ans:
            passed += 1
        else:
            print("Edge mismatch", inst, ec_ans, sat_ans)
            break
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
    print(result)

if __name__ == '__main__':
    run_tests()
