import itertools
import random
import json
from typing import List, Dict, Any

from problems import HamiltonianCycle, Sat
from reduce import reduce


def solve_hamiltonian(instance: Dict[str, Any]) -> bool:
    n = instance['n']
    edges = set()
    for u, v in instance['edges']:
        edges.add((u, v))
        edges.add((v, u))
    if n <= 2:
        return False
    # fix start at 0 to avoid rotations
    for perm in itertools.permutations(range(1, n)):
        path = (0,) + perm
        ok = True
        for i in range(n):
            u = path[i]
            v = path[(i + 1) % n]
            if (u, v) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat(instance: Dict[str, Any]) -> bool:
    m = instance['num_vars']
    clauses = instance['clauses']
    # empty clause => unsat
    for clause in clauses:
        if len(clause) == 0:
            return False
    # no clauses => sat
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
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


def random_graph(n: int, p: float = 0.5) -> Dict[str, Any]:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < p:
                edges.append([u, v])
    return {'n': n, 'edges': edges}


def run_tests(num_random: int = 200) -> Dict[str, int]:
    total = 0
    passed = 0
    # exhaustive for n<=4
    for n in range(0, 5):
        all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(all_edges)):
            edges = []
            for i, (u, v) in enumerate(all_edges):
                if mask & (1 << i):
                    edges.append([u, v])
            inst = {'n': n, 'edges': edges}
            HamiltonianCycle.validate(inst)
            h_yes = solve_hamiltonian(inst)
            sat_inst = reduce(inst)
            sat_yes = solve_sat(sat_inst)
            total += 1
            if h_yes == sat_yes:
                passed += 1
    # random tests up to n=4 (larger n would make the brute‑force SAT solver too slow)
    for _ in range(num_random):
        n = random.randint(0, 4)
        inst = random_graph(n, p=0.4)
        HamiltonianCycle.validate(inst)
        h_yes = solve_hamiltonian(inst)
        sat_inst = reduce(inst)
        sat_yes = solve_sat(sat_inst)
        total += 1
        if h_yes == sat_yes:
            passed += 1
    return {'total': total, 'passed': passed}

if __name__ == '__main__':
    result = run_tests()
    print('Tests run:', result['total'], 'Passed:', result['passed'])
    verified = result['total'] == result['passed']
    verdict = {
        'verified': verified,
        'tests_run': result['total'],
        'tests_passed': result['passed'],
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('Verdict written to verdict.json')
