import random
import itertools
import json
import sys
from problems import OneInThreeSat, SubsetSum
from reduce import reduce


def solve_one_in_three(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # iterate over assignments as bits 0..m-1
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            true_cnt = sum(1 for var in clause if (bits >> (var - 1)) & 1)
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    # early trivial cases
    if target == 0:
        return True
    if target < 0:
        return False
    for r in range(1, n + 1):
        for combo in itertools.combinations(range(n), r):
            s = sum(numbers[i] for i in combo)
            if s == target:
                return True
    return False


def random_one_in_three_instance(max_vars=5, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if clauses exist
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct vars from 1..max(m,3)
        if m < 3:
            # if not enough vars, set m to 3
            m = 3
        clause = random.sample(range(1, m + 1), 3)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    random.seed(0)
    tests = 200
    passed = 0
    for i in range(tests):
        inst = random_one_in_three_instance()
        # validate
        OneInThreeSat.validate(inst)
        reduced = reduce(inst)
        SubsetSum.validate(reduced)
        ans_src = solve_one_in_three(inst)
        ans_tgt = solve_subset_sum(reduced)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch on test", i)
            print("src", json.dumps(inst))
            print("reduced", json.dumps(reduced))
            print("src ans", ans_src, "tgt ans", ans_tgt)
            sys.exit(1)
    # edge cases
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
    ]
    for inst in edge_cases:
        OneInThreeSat.validate(inst)
        reduced = reduce(inst)
        SubsetSum.validate(reduced)
        if solve_one_in_three(inst) != solve_subset_sum(reduced):
            print("Edge case mismatch", inst, reduced)
            sys.exit(1)
        passed += 1
    total = tests + len(edge_cases)
    verdict = {"verified": True, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == '__main__':
    main()
