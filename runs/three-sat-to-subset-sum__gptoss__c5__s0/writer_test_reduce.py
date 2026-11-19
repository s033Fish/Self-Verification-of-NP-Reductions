import random
import itertools
import sys
from problems import ThreeSat, SubsetSum
from reduce import reduce

def solve_three_sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    if not clauses:
        return True
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1
                if lit > 0 and val == 1:
                    clause_ok = True
                if lit < 0 and val == 0:
                    clause_ok = True
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

def solve_subset_sum_bruteforce(instance):
    """DP based subset‑sum solver for non‑negative numbers.
    """
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for a in numbers:
        if target in reachable:
            return True
        new_sums = {s + a for s in reachable if s + a <= target}
        reachable.update(new_sums)
    return target in reachable

def random_three_sat(max_vars=4, max_clauses=4):
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        if m < 3:
            # generate a clause with distinct vars if possible, else skip
            if m == 0:
                continue
            vars = random.sample(range(1, m+1), k=m)
            # pad with repeats not allowed, so skip this clause
            continue
        vars = random.sample(range(1, m+1), k=3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def main():
    random.seed(0)
    tests = 200
    passed = 0
    for i in range(tests):
        inst = random_three_sat()
        ThreeSat.validate(inst)
        reduced = reduce(inst)
        SubsetSum.validate(reduced)
        ans1 = solve_three_sat_bruteforce(inst)
        ans2 = solve_subset_sum_bruteforce(reduced)
        if ans1 == ans2:
            passed += 1
        else:
            print("Mismatch!", inst, reduced, ans1, ans2)
            sys.exit(1)
    print(f"All {passed}/{tests} tests passed.")

if __name__ == "__main__":
    main()
