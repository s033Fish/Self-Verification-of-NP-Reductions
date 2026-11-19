import random
import itertools
import json
from problems import SubsetSum, Sat
from reduce import reduce

def subset_sum_bruteforce(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    # edge cases per definition
    if target == 0:
        return True
    if target < 0:
        return False
    # iterate subsets
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False

def sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # empty clause => unsat
    for clause in clauses:
        if len(clause) == 0:
            return False
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    return False

def test_random(num_tests=200):
    for _ in range(num_tests):
        n = random.randint(0, 5)
        numbers = [random.randint(0, 10) for _ in range(n)]
        target = random.randint(-5, 15)
        ss_instance = {"numbers": numbers, "target": target}
        # validate
        SubsetSum.validate(ss_instance)
        sat_instance = reduce(ss_instance)
        Sat.validate(sat_instance)
        ss_ans = subset_sum_bruteforce(ss_instance)
        sat_ans = sat_bruteforce(sat_instance)
        if ss_ans != sat_ans:
            print("Mismatch!", ss_instance, "=>", sat_instance)
            print("SS", ss_ans, "SAT", sat_ans)
            return False
    return True

def test_edge_cases():
    cases = [
        ({"numbers": [], "target": 0}, True),
        ({"numbers": [], "target": 5}, False),
        ({"numbers": [], "target": -3}, False),
        ({"numbers": [0,0,0], "target": 0}, True),
        ({"numbers": [5,7], "target": 12}, True),
        ({"numbers": [5,7], "target": 13}, False),
    ]
    for inst, expected in cases:
        SubsetSum.validate(inst)
        sat_inst = reduce(inst)
        Sat.validate(sat_inst)
        ss = subset_sum_bruteforce(inst)
        sat = sat_bruteforce(sat_inst)
        assert ss == expected, f"SubsetSum expected {expected} got {ss} for {inst}"
        assert sat == expected, f"SAT expected {expected} got {sat} for {inst}"

if __name__ == "__main__":
    ok = test_random()
    print("Random tests passed?", ok)
    test_edge_cases()
    print("Edge case tests passed.")
