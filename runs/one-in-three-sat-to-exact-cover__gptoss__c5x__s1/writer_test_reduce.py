import random
import itertools
import json
from problems import OneInThreeSat, ExactCover
from reduce import reduce


def solve_one_in_three_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if sum(bits[var-1] for var in clause) != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance):
    u = instance['universe_size']
    sets = instance['sets']
    # generate all subsets of indices
    n = len(sets)
    universe = set(range(u))
    for r in range(n+1):
        for combo in itertools.combinations(range(n), r):
            chosen = [sets[i] for i in combo]
            # check pairwise disjoint and cover
            covered = set()
            ok = True
            for s in chosen:
                sset = set(s)
                if covered & sset:
                    ok = False
                    break
                covered |= sset
            if ok and covered == universe:
                return True
    return False


def random_one_in_three_instance(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 if there are clauses
    num_clauses = random.randint(0, max_clauses)
    if num_clauses > 0 and m < 3:
        m = 3
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct vars from 1..m
        vars = random.sample(range(1, m+1), 3)
        random.shuffle(vars)
        clauses.append(vars)
    return {'num_vars': m, 'clauses': clauses}


def random_exact_cover_instance(max_u=4, max_sets=5):
    u = random.randint(0, max_u)
    sets = []
    for _ in range(random.randint(0, max_sets)):
        # random subset of universe
        subset = [i for i in range(u) if random.choice([True, False])]
        # ensure distinct elements already
        sets.append(subset)
    return {'universe_size': u, 'sets': sets}


def main():
    random.seed(0)
    tests = 200
    passed = 0
    for _ in range(tests):
        src = random_one_in_three_instance()
        # validate source
        OneInThreeSat.validate(src)
        reduced = reduce(src)
        ExactCover.validate(reduced)
        src_ans = solve_one_in_three_sat(src)
        tgt_ans = solve_exact_cover(reduced)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('src', src)
            print('reduced', reduced)
            print('src_ans', src_ans, 'tgt_ans', tgt_ans)
            break
    print('tests_run', tests, 'tests_passed', passed)
    # write verdict
    verdict = {'verified': passed == tests, 'tests_run': tests, 'tests_passed': passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    assert passed == tests, 'Not all tests passed'

if __name__ == '__main__':
    main()
