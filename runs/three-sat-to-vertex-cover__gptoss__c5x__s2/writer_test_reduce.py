import random
import itertools
import json
from problems import ThreeSat, VertexCover
from reduce import reduce


def solve_three_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
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


def solve_vertex_cover(instance):
    n = instance['n']
    edges = [(u, v) for u, v in instance['edges']]
    k = instance['k']
    if k < 0:
        return False
    if not edges:
        return True
    if k >= n:
        return True
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            s = set(subset)
            if all(u in s or v in s for u, v in edges):
                return True
    return False


def random_three_sat_instance(max_vars=3, max_clauses=3):
    """Generate a tiny random 3‑SAT instance for testing."""
    m = random.randint(0, max_vars)
    c = random.randint(0, max_clauses)
    if c > 0 and m < 3:
        m = 3
    clauses = []
    for _ in range(c):
        vars = random.sample(range(1, m + 1), 3)
        clause = [random.choice([1, -1]) * v for v in vars]
        clauses.append(clause)
    return {'num_vars': m, 'clauses': clauses}


def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        inst = random_three_sat_instance()
        ThreeSat.validate(inst)
        red = reduce(inst)
        VertexCover.validate(red)
        ans_src = solve_three_sat(inst)
        ans_tgt = solve_vertex_cover(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch!')
            print('Source:', inst)
            print('Reduced:', red)
            print('Source answer', ans_src, 'Target answer', ans_tgt)
            break
    return passed, num_trials

if __name__ == '__main__':
    passed, total = run_tests(500)
    result = {
        'verified': passed == total,
        'tests_run': total,
        'tests_passed': passed,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
