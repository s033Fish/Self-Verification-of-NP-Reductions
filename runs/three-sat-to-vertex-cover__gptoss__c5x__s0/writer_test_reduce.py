import itertools
import random
import json
from problems import ThreeSat, VertexCover
from reduce import reduce

def three_sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # iterate over all assignments 0..1 for each var (1-indexed)
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0 and val:
                    clause_ok = True
                if lit < 0 and not val:
                    clause_ok = True
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

def vertex_cover_bruteforce(instance):
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]
    # if k < 0 immediate false
    if k < 0:
        return False
    # check all subsets up to size k
    vertices = list(range(n))
    for r in range(k+1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            s = set(subset)
            for u, v in edges:
                if u not in s and v not in s:
                    covered = False
                    break
            if covered:
                return True
    return False

def random_three_sat(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure if clauses >0 then m>=3 as per edge case, but we allow 0.
    if m < 3:
        # no clauses allowed
        clauses = []
    else:
        num_clauses = random.randint(0, max_clauses)
        clauses = []
        for _ in range(num_clauses):
            # pick 3 distinct variables
            vars = random.sample(range(1, m+1), 3)
            clause = []
            for v in vars:
                lit = v if random.choice([True, False]) else -v
                clause.append(lit)
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        src = random_three_sat()
        # validate source
        ThreeSat.validate(src)
        tgt = reduce(src)
        VertexCover.validate(tgt)
        ans_src = three_sat_bruteforce(src)
        ans_tgt = vertex_cover_bruteforce(tgt)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", src, tgt, ans_src, ans_tgt)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests()
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
