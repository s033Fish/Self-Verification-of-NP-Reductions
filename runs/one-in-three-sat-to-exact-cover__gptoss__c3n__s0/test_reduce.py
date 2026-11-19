import random
import itertools
import json
from problems import OneInThreeSat, ExactCover
from reduce import reduce

def solve_one_in_three(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << m):
        assign = [(mask >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in clauses:
            if sum(assign[v-1] for v in clause) != 1:
                ok = False
                break
        if ok:
            return True
    return True if not clauses else False

def solve_exact_cover(instance):
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    # enumerate subsets of sets
    for r in range(1, n+1):
        for combo in itertools.combinations(range(n), r):
            covered = set()
            ok = True
            for idx in combo:
                s = sets[idx]
                # check disjointness
                if any(el in covered for el in s):
                    ok = False
                    break
                covered.update(s)
            if ok and covered == set(range(u)):
                return True
    # also handle empty universe
    if u == 0:
        return True
    return False


def random_one_in_three_instance(max_vars=5, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
    max_c = max_clauses
    clauses = []
    if m >= 3:
        num_clauses = random.randint(0, max_c)
        for _ in range(num_clauses):
            # pick 3 distinct vars from 1..m
            clause = random.sample(range(1, m+1), 3)
            clauses.append(clause)
    else:
        # if m <3, only allow empty clause list
        clauses = []
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        inst = random_one_in_three_instance()
        # validate source
        OneInThreeSat.validate(inst)
        red = reduce(inst)
        ExactCover.validate(red)
        ans_src = solve_one_in_three(inst)
        ans_red = solve_exact_cover(red)
        if ans_src == ans_red:
            passed += 1
        else:
            print("Mismatch!", inst, red, ans_src, ans_red)
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
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
