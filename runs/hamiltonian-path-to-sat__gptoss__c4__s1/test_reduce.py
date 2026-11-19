import itertools
import random
import json
import sys
from problems import HamiltonianPath, Sat
from reduce import reduce


def hamiltonian_path_bruteforce(instance):
    n = instance['n']
    edges = set()
    for u, v in instance['edges']:
        edges.add((u, v))
        edges.add((v, u))
    if n == 0:
        return False
    if n == 1:
        return True
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n - 1):
            if (perm[i], perm[i+1]) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for clause in clauses:
        if len(clause) == 0:
            return False
    for bits in range(1 << m):
        assign = [(bits >> i) & 1 == 1 for i in range(m)]
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


def generate_random_instance(n, edge_prob=0.5):
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {'n': n, 'edges': edges}


def run_tests():
    random.seed(0)
    total = 0
    passed = 0
    for n in range(0, 5):
        verts = list(range(n))
        possible_edges = [(u, v) for u in verts for v in verts if u < v]
        for mask in range(1 << len(possible_edges)):
            edges = []
            for i, (u, v) in enumerate(possible_edges):
                if mask & (1 << i):
                    edges.append([u, v])
            instance = {'n': n, 'edges': edges}
            HamiltonianPath.validate(instance)
            ans_h = hamiltonian_path_bruteforce(instance)
            reduced = reduce(instance)
            ans_sat = sat_bruteforce(reduced)
            total += 1
            if ans_h == ans_sat:
                passed += 1
            else:
                print('Mismatch! n', n, 'edges', edges, 'hp', ans_h, 'sat', ans_sat)
                return total, passed
    # also random tests for small n (where brute‑force SAT is feasible)
    for _ in range(50):
        n = random.randint(1, 4)
        inst = generate_random_instance(n, edge_prob=0.4)
        HamiltonianPath.validate(inst)
        ans_h = hamiltonian_path_bruteforce(inst)
        reduced = reduce(inst)
        ans_sat = sat_bruteforce(reduced)
        total += 1
        if ans_h == ans_sat:
            passed += 1
        else:
            print('Random mismatch! n', n, 'inst', inst, 'hp', ans_h, 'sat', ans_sat)
            return total, passed
    return total, passed

if __name__ == '__main__':
    total, passed = run_tests()
    print('Tests run:', total, 'passed:', passed)
    verdict = {
        'verified': total == passed,
        'tests_run': total,
        'tests_passed': passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    sys.exit(0 if total == passed else 1)
