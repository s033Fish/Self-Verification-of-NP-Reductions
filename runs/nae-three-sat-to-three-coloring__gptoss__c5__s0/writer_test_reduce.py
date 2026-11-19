import random
import itertools
import json
from problems import NaeThreeSat
from reduce import reduce

def solve_nae(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            vals = []
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1
                if lit < 0:
                    val = 1 - val
                vals.append(val)
            if all(v == 1 for v in vals) or all(v == 0 for v in vals):
                ok = False
                break
        if ok:
            return True
    return False

def solve_threecolor(instance):
    n = instance['n']
    edges = [(u, v) for u, v in instance['edges']]
    for colors in itertools.product(range(3), repeat=n):
        good = True
        for u, v in edges:
            if colors[u] == colors[v]:
                good = False
                break
        if good:
            return True
    return False

def random_instance(max_vars=3, max_clauses=3):
    """Generate a small random NAE‑3‑SAT instance.
    The sizes are limited so that the exhaustive 3‑coloring solver used in
    the test runs quickly.
    """
    m = random.randint(0, max_vars)
    if m > 0 and random.random() < 0.5:
        m = max(m, 3)
    clauses = []
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        if m < 3:
            break
        vars = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def main():
    tests = 200
    passed = 0
    for i in range(tests):
        inst = random_instance()
        NaeThreeSat.validate(inst)
        reduced = reduce(inst)
        ans1 = solve_nae(inst)
        ans2 = solve_threecolor(reduced)
        if ans1 == ans2:
            passed += 1
        else:
            print('Mismatch on instance', inst)
            print('Reduced', reduced)
            print('NAE answer', ans1, '3Color answer', ans2)
            break
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1,2,3]]},
        {"num_vars": 3, "clauses": [[1,2,-3]]},
    ]
    for ec in edge_cases:
        NaeThreeSat.validate(ec)
        reduced = reduce(ec)
        if solve_nae(ec) != solve_threecolor(reduced):
            print('Mismatch on edge case', ec)
            break
        else:
            passed += 1
    total = tests + len(edge_cases)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)

if __name__ == '__main__':
    main()
