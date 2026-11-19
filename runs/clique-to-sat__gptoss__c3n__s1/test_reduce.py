import random
import itertools
import json
from problems import Clique, Sat
from reduce import reduce

def solve_clique(instance):
    n = instance['n']
    edges = set()
    for u, v in instance['edges']:
        edges.add(frozenset((u, v)))
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    vertices = list(range(n))
    for size in range(k, n+1):
        for subset in itertools.combinations(vertices, size):
            if all(frozenset((u, v)) in edges for u, v in itertools.combinations(subset, 2)):
                return True
    return False

def solve_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for clause in clauses:
        if len(clause) == 0:
            return False
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in clauses:
            sat_clause = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0 and val:
                    sat_clause = True
                    break
                if lit < 0 and not val:
                    sat_clause = True
                    break
            if not sat_clause:
                ok = False
                break
        if ok:
            return True
    return False

def random_instance(max_n=3):
    n = random.randint(0, max_n)
    possible = [(i, j) for i in range(n) for j in range(i+1, n)]
    edges = []
    for (i, j) in possible:
        if random.choice([True, False]):
            edges.append([i, j])
    k = random.randint(-1, n+2)
    return {"n": n, "edges": edges, "k": k}

def main():
    random.seed(0)
    tests = 200
    passed = 0
    for _ in range(tests):
        inst = random_instance()
        Clique.validate(inst)
        sat_inst = reduce(inst)
        Sat.validate(sat_inst)
        ans1 = solve_clique(inst)
        ans2 = solve_sat(sat_inst)
        if ans1 == ans2:
            passed += 1
        else:
            print('Mismatch')
            print('Clique instance:', json.dumps(inst))
            print('SAT instance:', json.dumps(sat_inst))
            print('Clique answer', ans1, 'SAT answer', ans2)
            break
    print('Passed', passed, '/', tests)
    verdict = {"verified": passed == tests, "tests_run": tests, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
