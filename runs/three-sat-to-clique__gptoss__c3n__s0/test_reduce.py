import itertools
import random
import sys
from problems import ThreeSat, Clique
from reduce import reduce


def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # iterate over assignments 0..2^m-1
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1  # 1 means true
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


def solve_clique(instance):
    n = instance["n"]
    edges = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        edges.add((u, v))
    k = instance["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # check all subsets of size k (since we only need at least k, if any larger works also)
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for i in range(size):
                for j in range(i + 1, size):
                    a, b = subset[i], subset[j]
                    if a > b:
                        a, b = b, a
                    if (a, b) not in edges:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                return True
    return False


def random_three_sat(m, num_clauses):
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct variables
        vars = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        # random small instance
        m = random.randint(0, 4)
        # ensure at least 0 clauses
        num_clauses = random.randint(0, 4)
        # if clauses >0 ensure m>=3 as per spec, else adjust
        if num_clauses > 0 and m < 3:
            m = 3
        inst = random_three_sat(m, num_clauses)
        # validate
        ThreeSat.validate(inst)
        # reduce
        red = reduce(inst)
        Clique.validate(red)
        ans_src = solve_three_sat(inst)
        ans_tgt = solve_clique(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", inst, red, ans_src, ans_tgt)
            return False, passed
    return True, passed

if __name__ == "__main__":
    ok, passed = run_tests()
    total = 200
    if ok:
        print(f"All {passed}/{total} tests passed.")
        verdict = {"verified": True, "tests_run": total, "tests_passed": passed}
    else:
        print(f"Only {passed}/{total} tests passed.")
        verdict = {"verified": False, "tests_run": total, "tests_passed": passed}
    import json, pathlib
    pathlib.Path("verdict.json").write_text(json.dumps(verdict))
