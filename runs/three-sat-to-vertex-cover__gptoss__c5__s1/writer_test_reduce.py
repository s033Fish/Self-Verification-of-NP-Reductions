import itertools
import random
import json
import sys
from problems import ThreeSat, VertexCover
from reduce import reduce


def three_sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            satisfied = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0 and val:
                    satisfied = True
                if lit < 0 and not val:
                    satisfied = True
                if satisfied:
                    break
            if not satisfied:
                ok = False
                break
        if ok:
            return True
    return False


def vertex_cover_bruteforce(instance):
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]
    # if k < 0, always false
    if k < 0:
        return False
    # trivial yes cases
    if not edges:
        return True
    if k >= n:
        return True
    for r in range(k + 1):
        for combo in itertools.combinations(range(n), r):
            cover = set(combo)
            if all(u in cover or v in cover for u, v in edges):
                return True
    return False


def random_three_sat_instance(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses, per spec
    if m < 3:
        num_clauses = 0
    else:
        num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct vars
        vars = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        inst = random_three_sat_instance()
        # validate
        ThreeSat.validate(inst)
        reduced = reduce(inst)
        VertexCover.validate(reduced)
        ans_sat = three_sat_bruteforce(inst)
        ans_vc = vertex_cover_bruteforce(reduced)
        if ans_sat == ans_vc:
            passed += 1
        else:
            print("Mismatch!", inst, reduced, ans_sat, ans_vc, file=sys.stderr)
        total += 1
    print(json.dumps({"verified": passed == total, "tests_run": total, "tests_passed": passed}))

if __name__ == "__main__":
    main()
