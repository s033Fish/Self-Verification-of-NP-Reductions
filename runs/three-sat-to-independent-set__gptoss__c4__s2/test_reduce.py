import json
import random
import itertools
import sys
from problems import ThreeSat, IndependentSet
from reduce import reduce


def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # iterate over all assignments
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1  # zero based index
                val = (bits >> var) & 1
                if lit > 0 and val == 1:
                    clause_ok = True
                    break
                if lit < 0 and val == 0:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def solve_independent_set(instance):
    n = instance["n"]
    edges = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        edges.add((u, v))
    k = instance["k"]
    # early cases
    if k <= 0:
        return True
    if k > n:
        return False
    # brute force subsets
    for r in range(k, n + 1):
        for combo in itertools.combinations(range(n), r):
            ok = True
            for i in range(len(combo)):
                for j in range(i + 1, len(combo)):
                    if (combo[i], combo[j]) in edges or (combo[j], combo[i]) in edges:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                return True
    return False


def random_three_sat_instance(max_vars=4, max_clauses=3):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if we add clauses
    if m < 3:
        m = 3
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct variables
        vars_ = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    random.seed(0)
    total = 200
    passed = 0
    for i in range(total):
        inst = random_three_sat_instance()
        # validate
        ThreeSat.validate(inst)
        src_ans = solve_three_sat(inst)
        tgt = reduce(inst)
        IndependentSet.validate(tgt)
        tgt_ans = solve_independent_set(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch on instance", i, inst, "src", src_ans, "tgt", tgt_ans, file=sys.stderr)
            break
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
