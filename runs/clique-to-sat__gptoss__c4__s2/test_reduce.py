import random
import itertools
import json
from problems import Clique, InvalidInstance
from reduce import reduce


def clique_bruteforce(instance):
    n = instance['n']
    edges = set()
    for u, v in instance['edges']:
        if u > v:
            u, v = v, u
        edges.add((u, v))
    k = instance['k']
    # Edge cases
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                a, b = (u, v) if u < v else (v, u)
                if (a, b) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # Empty clause => unsat
    for clause in clauses:
        if len(clause) == 0:
            return False
    if not clauses:
        return True
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
                if lit > 0 and val:
                    clause_ok = True
                    break
                if lit < 0 and not val:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def random_instance(max_n=4):
    """Generate a small random Clique instance for testing."""
    n = random.randint(0, max_n)
    possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
    edges = []
    for (i, j) in possible:
        if random.choice([True, False]):
            edges.append([i, j])
    k = random.randint(-2, n + 1)  # may be <=0 or >n
    return {"n": n, "edges": edges, "k": k}


def main():
    total = 0
    passed = 0
    for _ in range(200):
        inst = random_instance()
        # ensure instance is valid
        try:
            Clique.validate(inst)
        except InvalidInstance:
            continue
        ans1 = clique_bruteforce(inst)
        red = reduce(inst)
        ans2 = sat_bruteforce(red)
        total += 1
        if ans1 == ans2:
            passed += 1
        else:
            print('Mismatch!')
            print('orig', inst, 'clique', ans1)
            print('sat', red, 'sat', ans2)
            break
    # explicit edge cases
    edge_cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": -5},
        {"n": 4, "edges": [], "k": 5},
        {"n": 2, "edges": [[0, 1]], "k": 2},
    ]
    for inst in edge_cases:
        Clique.validate(inst)
        ans1 = clique_bruteforce(inst)
        red = reduce(inst)
        ans2 = sat_bruteforce(red)
        total += 1
        if ans1 == ans2:
            passed += 1
        else:
            print('Edge case mismatch', inst, ans1, ans2)
    print('Tests run', total, 'passed', passed)
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
