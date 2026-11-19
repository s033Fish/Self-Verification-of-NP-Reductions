import random
import itertools
import json
import problems
from reduce import reduce

def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # iterate over all assignments
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1  # 1 means True
                if lit > 0 and val == 1:
                    sat = True
                if lit < 0 and val == 0:
                    sat = True
                if sat:
                    break
            if not sat:
                ok = False
                break
        if ok:
            return True
    return False

def solve_vertex_cover(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    # brute force subsets up to k
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            covered = set(subset)
            good = True
            for u, v in edges:
                if u not in covered and v not in covered:
                    good = False
                    break
            if good:
                return True
    return False

def random_three_sat(m, c):
    clauses = []
    for _ in range(c):
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
        m = random.randint(0, 4)
        # ensure if m<3 and clauses>0 then skip (invalid per spec). We'll generate c accordingly.
        max_clauses = 4
        c = random.randint(0, max_clauses)
        if c > 0 and m < 3:
            m = random.randint(3, 4)
        inst = random_three_sat(m, c)
        # validate
        problems.ThreeSat.validate(inst)
        vc = reduce(inst)
        problems.VertexCover.validate(vc)
        ans_sat = solve_three_sat(inst)
        ans_vc = solve_vertex_cover(vc)
        if ans_sat == ans_vc:
            passed += 1
        else:
            print("Mismatch!", inst, vc, ans_sat, ans_vc)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests(500)
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
