import itertools
import random
import json
from problems import ThreeSat, VertexCover
from reduce import reduce


def three_sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
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
                if clause_ok:
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def vertex_cover_bruteforce(instance):
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            s = set(subset)
            if all(u in s or v in s for u, v in edges):
                return True
    return False


def random_three_sat(max_vars=4, max_clauses=5):
    """Generate a random 3‑SAT instance respecting the problem constraints.

    The generator ensures that if there are any clauses then ``m >= 3`` so that
    we can pick three distinct variables per clause.
    """
    m = random.randint(0, max_vars)
    if m < 3:
        c = 0
    else:
        c = random.randint(0, max_clauses)
    clauses = []
    for _ in range(c):
        vars_ = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for i in range(num_tests):
        inst = random_three_sat()
        ThreeSat.validate(inst)
        src_ans = three_sat_bruteforce(inst)
        red = reduce(inst)
        VertexCover.validate(red)
        tgt_ans = vertex_cover_bruteforce(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch on instance", json.dumps(inst))
            print("Reduced", red)
            print("src", src_ans, "tgt", tgt_ans)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests()
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
