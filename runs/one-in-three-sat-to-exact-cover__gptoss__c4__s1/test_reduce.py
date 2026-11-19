import itertools
import random
import json
from problems import OneInThreeSat, ExactCover
from reduce import reduce

def solve_one_in_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # iterate over assignments as bits 0..(2^m-1)
    for bits in range(1 << m):
        # assignment dict var->bool
        assign = {i+1: bool(bits & (1 << i)) for i in range(m)}
        ok = True
        for clause in clauses:
            true_count = sum(assign[v] for v in clause)
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return False

def solve_exact_cover(instance):
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    universe = set(range(u))
    # iterate over subsets of sets
    for mask in range(1 << n):
        chosen = []
        covered = set()
        ok = True
        for i in range(n):
            if mask & (1 << i):
                s = set(sets[i])
                # disjointness check
                if covered & s:
                    ok = False
                    break
                covered |= s
                chosen.append(i)
        if not ok:
            continue
        if covered == universe:
            return True
    return False

def random_one_in_three_instance(max_vars=5, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 if clauses >0
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        if m == 0:
            # cannot create clause, break
            break
        # pick 3 distinct vars from 1..m
        clause = random.sample(range(1, m+1), 3) if m >= 3 else []
        if len(clause) == 3:
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def test_random_instances(num_trials=200):
    for _ in range(num_trials):
        inst = random_one_in_three_instance()
        # validate source
        OneInThreeSat.validate(inst)
        red = reduce(inst)
        ExactCover.validate(red)
        src_ans = solve_one_in_three_sat(inst)
        tgt_ans = solve_exact_cover(red)
        if src_ans != tgt_ans:
            print("Mismatch!", json.dumps(inst), json.dumps(red), src_ans, tgt_ans)
            return False
    return True

def test_edge_cases():
    # No clauses, any m
    for m in range(0,4):
        inst = {"num_vars": m, "clauses": []}
        OneInThreeSat.validate(inst)
        red = reduce(inst)
        ExactCover.validate(red)
        assert solve_one_in_three_sat(inst) == True
        assert solve_exact_cover(red) == (red["universe_size"] == 0)
    # Clause with variable not appearing elsewhere
    inst = {"num_vars": 3, "clauses": [[1,2,3]]}
    OneInThreeSat.validate(inst)
    red = reduce(inst)
    ExactCover.validate(red)
    assert solve_one_in_three_sat(inst) == True  # any assignment with exactly one true
    assert solve_exact_cover(red) == True
    return True

if __name__ == "__main__":
    ok = test_edge_cases() and test_random_instances()
    print("All tests passed" if ok else "Tests failed")
