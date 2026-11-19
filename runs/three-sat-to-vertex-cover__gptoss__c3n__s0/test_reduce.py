import random
import itertools
import json
from problems import ThreeSat, VertexCover
from reduce import reduce

def solve_three_sat(instance):
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

def solve_vertex_cover(instance):
    n = instance["n"]
    edges = instance["edges"]
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

def random_three_sat(m, num_clauses):
    clauses = []
    for _ in range(num_clauses):
        vars = random.sample(range(1, m+1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

random.seed(0)

tests = []
for m in range(1, 5):
    max_clauses = 4 if m >= 3 else 0
    for num_clauses in range(0, max_clauses + 1):
        for _ in range(20):
            inst = random_three_sat(m, num_clauses)
            ThreeSat.validate(inst)
            vc = reduce(inst)
            VertexCover.validate(vc)
            sat = solve_three_sat(inst)
            vc_yes = solve_vertex_cover(vc)
            if sat != vc_yes:
                print("Mismatch!", inst, vc)
                raise SystemExit(1)
            tests.append((inst, vc))
print(f"All {len(tests)} tests passed.")

verdict = {"verified": True, "tests_run": len(tests), "tests_passed": len(tests)}
with open('verdict.json', 'w') as f:
    json.dump(verdict, f)
